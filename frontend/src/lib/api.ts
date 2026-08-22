// Typed client for the live Atlas API (/api/digest, /api/feedback).

import type { Digest, FeedbackResponse, Reaction } from "./types";

const DIGEST_URL = "/api/digest";
const FEEDBACK_URL = "/api/feedback";

export async function fetchDigest(): Promise<Digest> {
  const res = await fetch(DIGEST_URL);
  if (!res.ok) throw new Error(`/api/digest → ${res.status}`);
  return res.json() as Promise<Digest>;
}

export async function postFeedback(
  itemType: string,
  itemId: string,
  reaction: Reaction
): Promise<FeedbackResponse> {
  const res = await fetch(FEEDBACK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      item_type: itemType,
      item_id: itemId,
      reaction,
    }),
  });
  if (!res.ok) throw new Error(`/api/feedback → ${res.status}`);
  return res.json() as Promise<FeedbackResponse>;
}
