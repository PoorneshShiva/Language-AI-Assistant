import React from 'react';

function ConjugationTable({ verb, level }) {
  const persons = ["ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie"];
  return (
    <div className="overflow-auto border border-gray-200 rounded-xl">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left p-2 font-semibold">Person</th>
            <th className="text-left p-2 font-semibold">Present</th>
            {level === "advanced" && <th className="text-left p-2 font-semibold">Simple past</th>}
            {level === "advanced" && <th className="text-left p-2 font-semibold">Past participle</th>}
          </tr>
        </thead>
        <tbody>
          {persons.map((p) => (
            <tr key={p} className="odd:bg-white even:bg-gray-50">
              <td className="p-2 whitespace-nowrap font-medium">{p}</td>
              <td className="p-2">{verb.present[p]}</td>
              {level === "advanced" && <td className="p-2">{verb.simple_past[p]}</td>}
              {level === "advanced" && (<td className="p-2">{verb.perfekt_aux} {verb.past_participle}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ConjugationTable;