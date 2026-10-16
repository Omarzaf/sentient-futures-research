import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

// Author acceptance applies only to the exact existing passages and interpretation.
// Source discovery, product approval and technical/legal claims remain separate.
export async function readReviewState(directory = import.meta.dirname) {
  let receipt;
  try {
    receipt = JSON.parse(await readFile(join(directory, 'author-review.json'), 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') return { status: 'pending', reviewed_claim_ids: [] };
    throw error;
  }
  if (receipt.status !== 'author_approved' || !receipt.author_statement_verbatim ||
      !Number.isFinite(Date.parse(receipt.recorded_at_utc)) ||
      receipt.review_scope !== 'existing_translations_and_religious_interpretations' ||
      receipt.independent_specialist_review_claimed !== false) {
    throw new Error('Invalid or overstated author review receipt');
  }
  const expectedFiles = ['claims.json', 'source-register.json', 'CHAPTER-DRAFT.md'];
  if (JSON.stringify(Object.keys(receipt.artifact_sha256).sort()) !==
      JSON.stringify(expectedFiles.toSorted())) throw new Error('Review artifact inventory changed');
  for (const name of expectedFiles) {
    const bytes = await readFile(join(directory, name));
    if (sha256(bytes) !== receipt.artifact_sha256[name]) {
      throw new Error(`Author review is stale for ${name}; review changed material separately`);
    }
  }
  const ledger = JSON.parse(await readFile(join(directory, 'claims.json'), 'utf8'));
  const intended = ledger.claims.filter(c => c.review_status === 'pending_qualified_human_review')
    .map(c => c.id).sort();
  const supplied = receipt.reviewed_claim_ids;
  if (!Array.isArray(supplied) || new Set(supplied).size !== supplied.length ||
      JSON.stringify(supplied.toSorted()) !== JSON.stringify(intended)) {
    throw new Error('Author review scope does not match the existing linguistic/religious claims');
  }
  if (receipt.market_estimates_approved !== false || receipt.publication_authorised !== false ||
      receipt.missing_sources_resolved !== false || receipt.policy_author_codes_supplied !== false) {
    throw new Error('Author review cannot waive unrelated evidence or approval gates');
  }
  return {
    status: receipt.status,
    reviewed_claim_ids: supplied,
    receipt: 'author-review.json',
    independent_specialist_review_claimed: false,
    remaining_claim_ids: ledger.claims.filter(c => !supplied.includes(c.id)).map(c => c.id),
  };
}
