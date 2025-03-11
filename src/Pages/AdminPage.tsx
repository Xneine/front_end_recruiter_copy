import { useState } from "react";
 import { Navbar } from "../components/Navbar/Navbar";
 import { MainContent } from "../components/MainContent/MainContent";
 
 export function AdminPage() {
   const [isCandidateSearch, setIsCandidateSearch] = useState(false);
 
   const handleToggle = () => {
     setIsCandidateSearch((prev) => !prev);
   };
 
   return (
     <div className="flex h-screen bg-gray-100">
       <div className="flex-1 flex flex-col">
         {/* Pass state dan handler ke Navbar */}
         <Navbar isCandidateSearch={isCandidateSearch} onToggle={handleToggle} />
         {/* Pass state ke MainContent */}
         <MainContent isCandidateSearch={isCandidateSearch} />
       </div>
     </div>
   );
 }