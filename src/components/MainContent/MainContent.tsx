import { Routes, Route } from "react-router-dom";
import { Chat } from "./content/Chat";
import { InformationChat } from "./content/InformationChat";

interface MainContentProps {
  isCandidateSearch: boolean;
}

export function MainContent({ isCandidateSearch }: MainContentProps) {
  return (
    <div className="flex-1 pt-6 overflow-y-auto">
      <Routes>
        <Route
          path="/chat"
          element={isCandidateSearch ? <Chat /> : <InformationChat />}
        />
      </Routes>
    </div>
  );
}
