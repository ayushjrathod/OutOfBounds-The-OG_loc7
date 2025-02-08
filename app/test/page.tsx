"use client";
import { useEffect, useState } from "react";

export default function TestPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:3000/api/db/manager", {
        method: "GET",
      });
      const result = await res.json();
      setData(result);
    };

    fetchData();
  }, []);

  return <div>{JSON.stringify(data)}</div>;
}
