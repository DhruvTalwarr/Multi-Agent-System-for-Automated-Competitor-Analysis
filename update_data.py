import sys
from utils.data_loader import build_dataset


def main():

    print("\n================= UPDATE DATA =================")

    query = " ".join(sys.argv[1:]).strip()

    if not query:
        query = None
        print("Mode: General dataset update")
    else:
        print("Mode: Query-based update")
        print(f"Query: {query}")

    try:
        build_dataset(query=query)
        print("✅ Update completed successfully")

    except Exception as e:
        print("❌ Update failed:", str(e))


if __name__ == "__main__":
    main()