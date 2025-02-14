import { Routes, Route } from "react-router-dom";
import { Chat } from "./content/Chat"

export function MainContent() {
  return (
    <div className="flex-1 pt-6 overflow-y-auto">
      <Routes>
        <Route path="/chat" element={<Chat/>}/>  
      </Routes>
    </div>
  );
}
