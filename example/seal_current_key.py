from kubernetes import client, config
from typing import Optional, List
from kubeseal_client import KubesealClient, SealedSecretsScope


class KubernetesManager:

    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def get_latest_key_name(self) -> str:
        print('List secrets')
        ret = self.v1.list_namespaced_secret(namespace='kube-system', label_selector='sealedsecrets.bitnami.com/sealed-secrets-key')
        newest = None
        for item in ret.items:
            if newest and item.metadata.creation_timestamp > newest.metadata.creation_timestamp:
                newest = item
            if not newest:
                newest = item
            print(
                "%s\t%s\t%s" %
                (item.metadata.namespace,
                item.metadata.name,
                item.metadata.creation_timestamp))
        print(
            "Newest: %s" %
            (newest.metadata.name))
        return newest.metadata.name

    def get_secrets_names(self, label: str, namespace: str) -> str:
        ret = self.v1.list_namespaced_secret(namespace=namespace, label_selector=label)
        names: List[str] = []
        for item in ret.items:
            names.append(item.metadata.name)
        return names

    def get_secret(self, name: str):
        return self.v1.read_namespaced_secret(name=name, namespace='kube-system')

    def get_sealed_secrets_controller(self):
        pods = self.v1.list_namespaced_pod(namespace='kube-system', label_selector='name=sealed-secrets-controller')
        if len(pods.items) != 1:
            print('WARN: There are multiple sealed secrets instances running!', len(pods.items))
        return pods.items[0]

def get_clean_secret(secret) -> dict:
    # Remove all unnecessary fields
    clean_secret: dict = {}
    clean_secret["api_version"] = secret.api_version
    clean_secret['kind'] = secret.kind
    clean_secret['type'] = secret.type
    clean_secret['data'] = secret.data
    clean_secret['metadata'] = {}
    clean_secret['metadata']['name'] = secret.metadata.name #+'-'+str(random.randint(1000,9999))
    clean_secret['metadata']['namespace'] = secret.metadata.namespace
    clean_secret['metadata']['labels'] = secret.metadata.labels
    clean_secret['metadata']['creation_timestamp'] = None
    return clean_secret

if __name__=="__main__":
    # inits
    kubernetes_manager: KubernetesManager = KubernetesManager()
    
    # get latest sealed secrets key from cluster
    latest_key_name: str = kubernetes_manager.get_latest_key_name()
    secret: bytes = kubernetes_manager.get_secret(latest_key_name)
    clean_secret: dict = get_clean_secret(secret)
    
    # seal the sealed secrets key
    scope: SealedSecretsScope = SealedSecretsScope.Cluster
    sealed_secret: bytes = KubesealClient.seal(clean_secret, scope=scope, output_format='json')
    # cert: str = 'cert.pem'
    # sealed_secret: bytes = KubesealClient.seal(clean_secret, pem_cert_file=cert, scope=scope, output_format='json')
    print(sealed_secret)
