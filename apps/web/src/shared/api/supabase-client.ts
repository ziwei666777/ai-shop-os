import { createBrowserClient } from "@supabase/ssr";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

export function createBrowserSupabaseClient() {
  // 登录页允许在未配置环境变量时展示表单，真正登录时再提示配置缺失。
  return createBrowserClient(supabaseUrl || "https://placeholder.supabase.co", supabaseAnonKey || "placeholder-key");
}
