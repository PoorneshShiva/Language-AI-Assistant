import React from 'react';

function CaseTable({ noun }) {
  const rows = [
    { k: "nominative", label: "Nominative" },
    { k: "accusative", label: "Accusative" },
    { k: "dative", label: "Dative" },
    { k: "genitive", label: "Genitive" },
  ];
  return (
    <div className="overflow-auto border border-gray-200 rounded-xl">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left p-2 font-semibold">Case</th>
            <th className="text-left p-2 font-semibold">Form</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.k} className="odd:bg-white even:bg-gray-50">
              <td className="p-2 whitespace-nowrap font-medium">{r.label}</td>
              <td className="p-2">{noun.caseForms[r.k]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CaseTable;
