import React from "react";

interface ToggleButtonProps {
  isCandidateSearch: boolean;
  onToggle: () => void;
}

export function ToggleButton({ isCandidateSearch, onToggle }: ToggleButtonProps) {
  return (
    <button
      onClick={onToggle}
      className={`px-4 py-2 rounded-lg border transition duration-300 ${
        isCandidateSearch ? "bg-green-500 text-white" : "bg-gray-200 text-black"
      }`}
    >
      {isCandidateSearch ? "Candidate Searching" : "Information Searching"}
    </button>
  );
}
