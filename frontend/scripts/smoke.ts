import React from "react";
import { renderToString } from "react-dom/server";

import KpiCard from "../components/KpiCard";
import ListCard from "../components/ListCard";
import HandoversTable from "../components/HandoversTable";

function runSmokeTest() {
  const markup = renderToString(
    <div>
      <KpiCard title="Total Revenue" current={12000} previous={10000} change={20} format="currency" />
      <ListCard
        title="Top Items"
        items={[
          { label: "Chef's Special", value: "12" },
          { label: "Signature Cocktail", value: "9" },
        ]}
      />
      <HandoversTable
        handovers={[
          {
            id: 1,
            outlet: "Main Restaurant",
            date: new Date().toISOString(),
            shift: "PM",
            period: "DINNER",
            bookings: 20,
            walk_ins: 10,
            covers: 75,
            food_revenue: 4200,
            beverage_revenue: 1800,
            top_sales: ["Chef's Special", "Seasonal Dessert"],
          },
        ]}
      />
    </div>
  );

  if (!markup) {
    throw new Error("Smoke test failed: markup is empty");
  }

  console.log("Smoke test rendered successfully.");
}

runSmokeTest();
