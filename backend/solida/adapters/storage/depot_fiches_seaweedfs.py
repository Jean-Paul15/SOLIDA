import io
from dataclasses import dataclass

from minio import Minio


@dataclass(frozen=True)
class DepotFichesSeaweedfs:
    """Implémente `DepotFiches` contre la passerelle S3 de SeaweedFS — pas MinIO, mais la
    même API S3 : `minio` (client Python) fonctionne contre n'importe quel service
    compatible S3, pas seulement MinIO lui-même. Voir
    `docs/backend/03-decisions-provisoires-a-revoir.md` pour le choix de SeaweedFS."""

    client: Minio
    bucket: str

    def __post_init__(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def archiver(self, chemin_objet: str, contenu: bytes) -> None:
        self.client.put_object(
            self.bucket,
            chemin_objet,
            io.BytesIO(contenu),
            length=len(contenu),
            content_type="application/pdf",
        )
