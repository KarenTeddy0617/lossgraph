from app.db.session import SessionLocal
from app.graph.builder import build_transaction_graph


def main():

    db = SessionLocal()

    try:

        graph = build_transaction_graph(db)

        print("Graph built successfully!")

        print("Number of nodes:", len(graph))

        total_edges = sum(
            len(neighbors)
            for neighbors in graph.values()
        ) // 2

        print("Number of edges:", total_edges)

        print("\nSample nodes:")

        for node, neighbors in list(graph.items())[:5]:

            print(
                f"{node} -> "
                f"{len(neighbors)} connections"
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()