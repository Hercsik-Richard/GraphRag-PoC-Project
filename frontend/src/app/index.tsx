import { RouterProvider } from "react-router-dom";
import { router } from "./router";

/**
 * Main application component
 */
export function App() {
  return <RouterProvider router={router} />;
}
