import { NextRequest } from "next/server";
import { setWebhook, deleteWebhook, getWebhookInfo } from "@/lib/telegram";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, webhookUrl } = body;

    if (action === "set") {
      if (!webhookUrl) {
        return Response.json({ error: "webhookUrl is required" }, { status: 400 });
      }
      const result = await setWebhook(webhookUrl);
      return Response.json(result);
    }

    if (action === "delete") {
      const result = await deleteWebhook();
      return Response.json(result);
    }

    if (action === "info") {
      const result = await getWebhookInfo();
      return Response.json(result);
    }

    return Response.json({ error: "Invalid action. Use: set, delete, info" }, { status: 400 });
  } catch (error) {
    console.error("Setup error:", error);
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function GET() {
  try {
    const result = await getWebhookInfo();
    return Response.json(result);
  } catch (error) {
    console.error("Webhook info error:", error);
    return Response.json({ error: "Failed to get webhook info" }, { status: 500 });
  }
}
