"""Explicitly billed synthetic-only Bedrock test; never sends patient data."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / '.env', override=False)

from vaidya.providers import BedrockConverseProvider, bedrock_settings

SYNTHETIC_TEXT = (
    'Synthetic test only. Specimen: appendix. Dictated finding: acute appendicitis. '
    'Please bold acute appendicitis. The temperature was not provided.'
)


def main():
    parser = argparse.ArgumentParser(description='Run a paid synthetic Bedrock extraction request')
    parser.add_argument('--confirm-cost', action='store_true', help='Explicitly authorize an AWS Bedrock request')
    args = parser.parse_args()
    s = bedrock_settings()
    print(f"Region: {s['region']} | Model: {s['model']}")
    print(f"Bearer token present: {s['credential_configured']} (token value never printed)")
    print(f"Structured output requested: {s['structured_output']}")
    if not args.confirm_cost:
        print('No request sent. Add --confirm-cost to make one billed synthetic request.')
        return 2
    if not s['remote_opt_in']:
        print('No request sent: set ALLOW_REMOTE_SYNTHETIC_INPUT=true in .env')
        return 2
    if not s['credential_configured'] and not os.getenv('AWS_PROFILE') and not os.getenv('AWS_ACCESS_KEY_ID'):
        print('No Bedrock credentials configured. Set AWS_BEARER_TOKEN_BEDROCK or use an authorized AWS profile/role.')
        return 2
    try:
        result = BedrockConverseProvider().extract(SYNTHETIC_TEXT)
    except Exception as exc:
        # Do not print exception strings because SDK exception messages could
        # contain sensitive request details. Model/region is already visible.
        print('Bedrock request failed:', type(exc).__name__)
        print('Check model ID, inference profile, Converse support, IAM, network, and region routing.')
        return 1
    print(f'PASS: real Bedrock extraction | {result.provider} | {result.model}')
    print(f'Latency: {result.latency_ms} ms | Usage: {result.usage}')
    print('Synthetic findings:', len(result.findings), '| format instructions:', len(result.instructions))
    print('All generated clinical content requires doctor review; no actual patient data was transmitted.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
