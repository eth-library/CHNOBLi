import json
import sys
import os
import argparse
import urllib.error
import urllib.request

# Path to the registry
REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "data_links.json")
API_BASE = "https://www.research-collection.ethz.ch/server/api"


def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def get_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; CHNOBLi/1.0)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def resolve_doi_to_files(doi):
    """
    Uses the DSpace 7 REST API to find all download links for a given DOI.
    Returns a dictionary of {filename: download_url}
    """
    try:
        # 1. Resolve DOI to Item
        pid_url = f"{API_BASE}/pid/find?id={doi.replace('https://doi.org/', '')}"
        item_data = get_json(pid_url)

        # 2. Get Bundles link
        bundles_url = item_data.get("_links", {}).get("bundles", {}).get("href")
        if not bundles_url:
            return {}

        # 3. Get Bundles and find ORIGINAL
        bundles = get_json(bundles_url).get("_embedded", {}).get("bundles", [])

        bitstreams_url = None
        for bundle in bundles:
            if bundle.get("name") == "ORIGINAL":
                bitstreams_url = (
                    bundle.get("_links", {}).get("bitstreams", {}).get("href")
                )
                break

        if not bitstreams_url:
            return {}

        # 4. Get Bitstreams
        bitstreams = get_json(bitstreams_url).get("_embedded", {}).get("bitstreams", [])

        file_map = {}
        for bs in bitstreams:
            name = bs.get("name")
            download_url = bs.get("_links", {}).get("content", {}).get("href")
            if name and download_url:
                file_map[name] = download_url

        return file_map

    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as e:
        print(f"API Error resolving DOI {doi}: {e}", file=sys.stderr)
        return {}


def main():
    parser = argparse.ArgumentParser(
        description="Resolve CHNOBLi data DOIs to download links using official API."
    )
    parser.add_argument(
        "--component", help="The component (e.g., milvus, elasticsearch, models)"
    )
    parser.add_argument(
        "--file", help="The specific file key (e.g., gnd_people, part_1)"
    )
    parser.add_argument(
        "--resolve-doi", help="Resolve a DOI URL dynamically and print found files"
    )

    args = parser.parse_args()

    if args.resolve_doi:
        files = resolve_doi_to_files(args.resolve_doi)
        if files:
            for name, url in files.items():
                print(f"{name}: {url}")
        else:
            print("No files found via API.")
        return

    if args.component and args.file:
        registry = load_registry()
        doi = registry.get(args.component, {}).get("doi")

        if doi:
            # Try API first
            files = resolve_doi_to_files(doi)
            # Find the filename we expect from the registry
            target_filename = registry[args.component]["files"][args.file].get(
                "filename"
            )

            if target_filename in files:
                print(files[target_filename])
                return

            # Fallback to hardcoded bitstream_id if API fails or file not found
            bitstream_id = registry[args.component]["files"][args.file].get(
                "bitstream_id"
            )
            if bitstream_id:
                print(
                    f"https://www.research-collection.ethz.ch/server/api/core/bitstreams/{bitstream_id}/content"
                )
                return

        print(
            f"Error: Could not resolve link for {args.component}/{args.file}.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
