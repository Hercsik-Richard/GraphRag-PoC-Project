import { createBrowserRouter, Navigate } from "react-router-dom";

/**
 * Application router configuration
 */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/chat" replace />,
  },
  {
    path: "/chat",
    lazy: async () => {
      const { ChatPage } = await import("@/pages/chat/ui/ChatPage");
      return { Component: ChatPage };
    },
  },
  {
    path: "*",
    element: <Navigate to="/chat" replace />,
  },
]);
