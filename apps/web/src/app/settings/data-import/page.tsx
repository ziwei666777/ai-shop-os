import { DataImportView } from "@/features/settings/data-import-view";
import { listImportJobsForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function DataImportPage() {
  const jobs = await listImportJobsForPage();
  return <AppShell><DataImportView initialJobs={jobs} /></AppShell>;
}
