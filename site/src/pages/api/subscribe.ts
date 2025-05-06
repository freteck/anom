// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === "POST") {
    let email = JSON.parse(req.body).email
    console.log(JSON.stringify({
      address: email
    }))
    await fetch("http://localhost:8000/subscribe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        address: email
      })
    });
    return res.status(200).json({ status: "Subscribed." });
  }
  return res.status(405);
}
