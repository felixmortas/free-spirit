import uuid
import numpy as np
import redis

from redisvl.schema import IndexSchema
from redisvl.index import SearchIndex
from redis.commands.search.query import Query


class RedisVectorDB:
    def __init__(self, schema_path="ingestion/schema/index.yaml", host="localhost", port=6379):
        # Connexion Redis
        self.redis_client = redis.Redis(host=host, port=port)

        # Chargement du schéma RedisVL depuis le YAML
        self.schema = IndexSchema.from_yaml(schema_path)
        self.index_name = self.schema.index.name
        self.prefix = self.schema.index.prefix
        self.key_separator = self.schema.index.key_separator

        # Création de l'index via RedisVL
        self.index = SearchIndex(schema=self.schema, redis_client=self.redis_client)
        self._create_index()

    def _create_index(self):
        """Crée l'index s'il n'existe pas déjà."""
        try:
            self.index.create(overwrite=False)
            print(f"Index '{self.index_name}' créé avec succès.")
        except Exception as e:
            print(f"Index '{self.index_name}' déjà existant ou erreur : {e}")

    def add(self, texts: list[str], vectors: list[list[float]]):
        """
        Insère des documents dans Redis via pipeline.

        Args:
            texts:   Liste de textes à stocker dans le champ 'content'.
            vectors: Liste de vecteurs (même longueur que texts, dim=1024).
        """
        if len(texts) != len(vectors):
            raise ValueError(f"texts et vectors doivent avoir la même longueur "
                             f"({len(texts)} vs {len(vectors)})")

        pipeline = self.redis_client.pipeline()

        for text, vec in zip(texts, vectors):
            doc_id = str(uuid.uuid4())
            # RedisVL construit la clé : {prefix}{key_separator}{id}
            # ex: "doc:550e8400-e29b-..."
            key = f"{self.prefix}{self.key_separator}{doc_id}"

            vec_bytes = np.array(vec, dtype=np.float32).tobytes()

            pipeline.hset(key, mapping={
                "content": text,
                "embedding": vec_bytes,
            })

        pipeline.execute()
        print(f"{len(texts)} document(s) insérés.")

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """
        Recherche les top_k documents les plus proches du vecteur requête.

        Args:
            query_vector: Vecteur de la requête (dim=1024, même modèle que l'indexation).
            top_k:        Nombre de résultats à retourner.

        Returns:
            Liste de dicts avec les champs 'id', 'content' et 'score'.
            Le score est dans [0, 1] — plus il est proche de 1, plus c'est similaire.
        """
        query_bytes = np.array(query_vector, dtype=np.float32).tobytes()

        q = (
            Query(f"(*)=>[KNN {top_k} @embedding $query_vector AS vector_score]")
            .sort_by("vector_score")
            .return_fields("content", "vector_score")
            .dialect(2)
        )

        results = self.redis_client.ft(self.index_name).search(
            q, {"query_vector": query_bytes}
        )

        return [
            {
                "id": doc.id,
                "content": doc.content,
                # cosine distance ∈ [0, 2] → on ramène en similarité ∈ [-1, 1]
                # Redis retourne la distance, donc 1 - distance ≈ similarité cosinus
                "score": round(1 - float(doc.vector_score), 4),
            }
            for doc in results.docs
        ]

    def delete_index(self):
        """Supprime l'index Redis (les données HASH ne sont pas supprimées)."""
        self.index.delete()
        print(f"Index '{self.index_name}' supprimé.")

    def flush_data(self):
        """Supprime toutes les clés correspondant au préfixe (données + index)."""
        pattern = f"{self.prefix}{self.key_separator}*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
            print(f"{len(keys)} clé(s) supprimée(s).")
        else:
            print("Aucune clé à supprimer.")