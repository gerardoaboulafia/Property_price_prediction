import os
import subprocess

def run_mlflow():
    # Configuración compartida (ajustar si cambia usuario/contraseña)
    backend_store = "mysql+pymysql://labo_ame_agus:ameagusmica@localhost:3307/laboratorioII"
    artifact_root = os.path.abspath("mlruns")

    cmd = [
        "python", "-m", "mlflow", "server",
        "--backend-store-uri", backend_store,
        "--default-artifact-root", f"file:///{artifact_root}",
        "--host", "localhost",
        "--port", "5000"
    ]

    print("Iniciando servidor MLflow...")
    subprocess.run(cmd)

if __name__ == "__main__":
    run_mlflow()
