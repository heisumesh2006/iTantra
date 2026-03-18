export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 180000);
  try {
    const response = await fetch("/api/v1" + path, {
      ...options,
      signal: controller.signal,
      headers:
        options.body instanceof FormData
          ? options.headers
          : { "Content-Type": "application/json", ...options.headers },
    });
    let content;
    try {
      content = await response.json();
    } catch {
      throw new Error(
        `Backend unavailable or returned an invalid response (HTTP ${response.status}). Check scripts/start-backend.ps1.`,
      );
    }
    if (!response.ok)
      throw new Error(
        content.error?.message ||
          (Array.isArray(content.detail)
            ? content.detail.map((d: { msg: string }) => d.msg).join("; ")
            : content.detail) ||
          "Request failed",
      );
    return content as T;
  } catch (error) {
    if (error instanceof TypeError)
      throw new Error(
        "Backend is offline. Start scripts/start-backend.ps1 and retry.",
      );
    if (error instanceof DOMException && error.name === "AbortError")
      throw new Error(
        "Request timed out. Check the backend status before retrying.",
      );
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
export function message(error: unknown) {
  return error instanceof Error ? error.message : "Unexpected processing error";
}