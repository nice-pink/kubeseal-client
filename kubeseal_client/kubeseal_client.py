from typing import Optional, List
from enum import Enum
import json
import subprocess

class SealedSecretsScope(Enum):
    Strict = 0
    Namespace = 1
    Cluster = 2

    @staticmethod
    def get_name(value: int):
        if value == SealedSecretsScope.Namespace:
            return "namespace-wide"
        elif value == SealedSecretsScope.Cluster:
            return "cluster-wide"
        else:
            return "strict"

class KubesealClient:

    @staticmethod
    def seal(secret: dict,
             output_file: Optional[str] = None,
             output_format: str = 'yaml',
             pem_cert_file: Optional[str] = None,
             scope: SealedSecretsScope = SealedSecretsScope.Strict,
             controller_name: Optional[str] = None) -> bytes:
        json_string: str = json.dumps(secret)
        echo = subprocess.Popen(('echo', json_string), stdout=subprocess.PIPE)
        
        command: List[str] = KubesealClient.get_seal_command(output_format=output_format,
                                                                  pem_cert_file=pem_cert_file,
                                                                  scope=scope,
                                                                  controller_name=controller_name)

        # kubeseal
        kubeseal = subprocess.Popen(command, stdin=echo.stdout, stdout=subprocess.PIPE)
        echo.stdout.close()

        # output bytes
        if not output_file:
            sealed_secret: bytes = kubeseal.stdout.read()
            kubeseal.stdout.close()
            return sealed_secret

        # save sealed secret to file and return output
        tee = subprocess.Popen(('tee', output_file), stdin=kubeseal.stdout, stdout=subprocess.PIPE)
        kubeseal.stdout.close()
        sealed_secret: bytes = tee.stdout.read()
        tee.stdout.close()
        return sealed_secret

    @staticmethod
    def seal_raw(raw_from_file: str,
                 output_file: Optional[str] = None,
                 output_format: str = 'yaml',
                 pem_cert_file: Optional[str] = None,
                 scope: SealedSecretsScope = SealedSecretsScope.Strict,
                 controller_name: Optional[str] = None) -> bytes:
        command: List[str] = KubesealClient.get_seal_command(raw_from_file=raw_from_file,
                                                                  output_format=output_format,
                                                                  pem_cert_file=pem_cert_file,
                                                                  scope=scope,
                                                                  controller_name=controller_name)

        # kubeseal
        kubeseal = subprocess.Popen(command, stdout=subprocess.PIPE)

        # output bytes
        if not output_file:
            sealed_secret: bytes = kubeseal.stdout.read()
            kubeseal.stdout.close()
            return sealed_secret

        # save sealed secret to file and return output
        tee = subprocess.Popen(('tee', output_file), stdin=kubeseal.stdout, stdout=subprocess.PIPE)
        kubeseal.stdout.close()
        sealed_secret: bytes = tee.stdout.read()
        tee.stdout.close()
        return sealed_secret

    @staticmethod
    def get_seal_command(output_format: str = 'yaml',
                         pem_cert_file: Optional[str] = None,
                         scope: SealedSecretsScope = SealedSecretsScope.Strict,
                         controller_name: Optional[str] = None,
                         raw_from_file: Optional[str] = None) -> str:
        command: List[str] = ['kubeseal', '--format', output_format]
        if pem_cert_file:
            command.extend(['--cert', pem_cert_file])
        if scope != SealedSecretsScope.Strict:
            command.extend(['--scope', SealedSecretsScope.get_name(scope)])
        if controller_name:
            command.extend(['--controller-name', controller_name])
        if raw_from_file:
            from_file: str = '--from-file=' + raw_from_file
            command.extend(['--raw', from_file])
        print('Seal command:', command)
        return command

    @staticmethod
    def fetch_cert(output_file: Optional[str] = None) -> bytes:
        echo = subprocess.Popen(('kubeseal', '--fetch-cert'), stdout=subprocess.PIPE)
        cert: str = echo.stdout.read()
        echo.stdout.close()

        if not output_file:
            return cert

        with open(output_file, 'wb') as file:
            file.write(cert)

        return cert
