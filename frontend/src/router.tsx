import { createBrowserRouter } from "react-router-dom";
import { Layout } from "./components/shared/Layout";
import { PromptsPage } from "./pages/PromptsPage";
import { CreatePromptPage } from "./pages/CreatePromptPage";
import { PromptDetailPage } from "./pages/PromptDetailPage";
import { EditPromptPage } from "./pages/EditPromptPage";
import { DashboardPage } from "./pages/DashboardPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <PromptsPage /> },
      { path: "prompts/new", element: <CreatePromptPage /> },
      { path: "prompts/:promptId", element: <PromptDetailPage /> },
      { path: "prompts/:promptId/edit", element: <EditPromptPage /> },
      { path: "dashboard", element: <DashboardPage /> },
    ],
  },
]);
