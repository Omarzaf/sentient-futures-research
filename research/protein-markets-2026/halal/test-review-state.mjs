import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, copyFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { readReviewState } from './review-state.mjs';

async function fixture() {
  const directory = await mkdtemp(join(tmpdir(), 'protein-author-review-'));
  for (const name of ['claims.json', 'source-register.json', 'CHAPTER-DRAFT.md', 'author-review.json']) {
    await copyFile(join(import.meta.dirname, name), join(directory, name));
  }
  return directory;
}

async function changeReceipt(directory, mutate) {
  const file = join(directory, 'author-review.json');
  const receipt = JSON.parse(await readFile(file, 'utf8'));
  mutate(receipt);
  await writeFile(file, JSON.stringify(receipt));
}

test('recorded approval covers only the six existing linguistic/religious claims', async () => {
  const result = await readReviewState(await fixture());
  assert.equal(result.status, 'author_approved');
  assert.equal(result.reviewed_claim_ids.length, 6);
  assert.equal(result.remaining_claim_ids.length, 3);
  assert.equal(result.independent_specialist_review_claimed, false);
});

test('changed translation cannot inherit earlier author acceptance', async () => {
  const directory = await fixture();
  const file = join(directory, 'claims.json');
  const ledger = JSON.parse(await readFile(file, 'utf8'));
  ledger.claims[0].draft_translation = 'A changed interpretation';
  await writeFile(file, JSON.stringify(ledger));
  await assert.rejects(readReviewState(directory), /stale/);
});

test('new or broadened claim IDs cannot inherit approval', async () => {
  const directory = await fixture();
  await changeReceipt(directory, r => r.reviewed_claim_ids.push('HALAL-REGISTERS-SCOPE'));
  await assert.rejects(readReviewState(directory), /scope/);
});

test('duplicate IDs cannot manufacture complete review', async () => {
  const directory = await fixture();
  await changeReceipt(directory, r => r.reviewed_claim_ids[1] = r.reviewed_claim_ids[0]);
  await assert.rejects(readReviewState(directory), /scope/);
});

test('acceptance cannot become publication permission or an expert credential', async () => {
  for (const field of ['publication_authorised', 'independent_specialist_review_claimed']) {
    const directory = await fixture();
    await changeReceipt(directory, r => r[field] = true);
    await assert.rejects(readReviewState(directory));
  }
});

test('missing receipt retains pending status', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'protein-no-review-'));
  assert.deepEqual(await readReviewState(directory), { status: 'pending', reviewed_claim_ids: [] });
});
