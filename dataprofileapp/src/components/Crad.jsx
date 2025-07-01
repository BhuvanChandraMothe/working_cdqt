import React from "react";

export const Card = ({ children }) => (
  <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-4">
    {children}
  </div>
);

export const CardContent = ({ children }) => (
  <div className="p-2">
    {children}
  </div>
);
