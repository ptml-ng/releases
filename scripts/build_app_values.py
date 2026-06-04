#!/usr/bin/env python3
"""Modern KMP build values for the ptml-ng/releases reusable workflows.

Usage:
    build_app_values.py <serverFlavour> [companyName] [packageName] [--target android|desktop]

Resolves company/server → package id (mirroring the `AndroidLibraryConfigurer.setupAppPackaging`
rule: `applicationId = app.id + (".$server" when server != "prod")`), looks up the Firebase
`mobilesdk_app_id` (android only) in `apps/android/google-services.json`, and emits one
`KEY=VALUE` per line to `$GITHUB_OUTPUT` via `write_output.py`.

Target switch:
    android (default) → :apps:android:assembleRelease  -Pcompany=…  -Pserver=…
                        PATH=apps/android/build/outputs/apk/release
    desktop           → :apps:desktop:packageMsi       -Pcompany=…  -Pserver=…
                        PATH=apps/desktop/build/compose/binaries/main/msi   (Windows only)
"""
import argparse
import json
import sys

from write_output import write_output

ANDROID_GOOGLE_SERVICES = "apps/android/google-services.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit build values for the flavorless KMP app.")
    parser.add_argument("server_flavour")
    parser.add_argument("company_name", nargs="?", default=None)
    parser.add_argument("package_name", nargs="?", default=None)
    parser.add_argument("--target", choices=("android", "desktop"), default="android")
    args = parser.parse_args()

    server = (args.server_flavour or "").strip()
    company = args.company_name.strip() if args.company_name else None
    package = args.package_name.strip() if args.package_name else None
    target = args.target

    if not server:
        print("server-flavour is required (dev/staging/prod).", file=sys.stderr)
        return 1

    # Resolve company → app.id from config.json (mirrors the app's own resolveFlavor logic).
    if company:
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            print(f"Failed to read config.json: {e}", file=sys.stderr)
            return 2

        match = next(
            (c for c in cfg.get("companies", []) if company.lower() in c.get("id", "").lower()),
            None,
        )
        if match is None:
            print(f"No company found with name {company}", file=sys.stderr)
            return 3
        company = match.get("id")
        if not package:
            package = match.get("app", {}).get("id")
            if not package:
                print(f"Company {company} has no app.id in config.json", file=sys.stderr)
                return 5

    if not package:
        print("Package name must come from company config or be passed explicitly.", file=sys.stderr)
        return 5

    # `applicationIdSuffix = ".${server}"` when server != prod — match the AGP convention.
    if server.lower() != "prod":
        package = f"{package}.{server.lower()}"

    # Firebase APP_ID lookup (android only). Compose Desktop has no Firebase App Distribution path.
    app_id = ""
    if target == "android":
        try:
            with open(ANDROID_GOOGLE_SERVICES, "r", encoding="utf-8") as f:
                gs = json.load(f)
        except Exception as e:
            print(f"Failed to read {ANDROID_GOOGLE_SERVICES}: {e}", file=sys.stderr)
            return 4

        client = next(
            (
                c for c in gs.get("client", [])
                if c.get("client_info", {}).get("android_client_info", {}).get("package_name") == package
            ),
            None,
        )
        if client is None:
            print(
                f"No client in {ANDROID_GOOGLE_SERVICES} with package_name={package}",
                file=sys.stderr,
            )
            return 6
        app_id = client.get("client_info", {}).get("mobilesdk_app_id", "")
        if not app_id:
            print("Matched client missing mobilesdk_app_id", file=sys.stderr)
            return 7

    company_flag = f" -Pcompany={company}" if company else ""
    server_flag = f" -Pserver={server}"

    if target == "android":
        build_command = f":apps:android:assembleRelease{company_flag}{server_flag}"
        path = "apps/android/build/outputs/apk/release"
    else:  # desktop
        build_command = f":apps:desktop:packageMsi{company_flag}{server_flag}"
        path = "apps/desktop/build/compose/binaries/main/msi"

    write_output([
        f"PACKAGE_NAME={package}",
        f"PATH={path}",
        f"BUILD_COMMAND={build_command}",
        f"APP_ID={app_id}",
    ])
    return 0


if __name__ == "__main__":
    sys.exit(main())
