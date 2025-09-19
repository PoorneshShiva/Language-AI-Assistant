import React from 'react';

function Section({ title, subtitle, children, right }) {
  return (
    <section className="bg-white rounded-xl shadow-md p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">{title}</h2>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        {right}
      </div>
      <div>{children}</div>
    </section>
  );
}

export default Section;