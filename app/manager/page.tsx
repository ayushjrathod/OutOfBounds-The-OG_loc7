"use client";
import { ExpenseList2 } from "@/components/ExpenseList2";
import { Card, CardContent } from "@/components/ui/card";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import {
  IconArrowLeft,
  IconBrandTabler,
  IconChevronLeft,
  IconChevronRight,
  IconSettings,
  IconUserBolt,
} from "@tabler/icons-react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
// Import Tabs components from shadcn UI
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function UserDashboard() {
  const [open, setOpen] = useState(false);
  const links = [
    {
      label: "Dashboard",
      href: "/manager",
      icon: <IconBrandTabler className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: "Profile",
      href: "#",
      icon: <IconUserBolt className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: "Settings",
      href: "#",
      icon: <IconSettings className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: "Logout",
      href: "#",
      icon: <IconArrowLeft className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />,
    },
  ];

  return (
    <div
      className={cn(
        "rounded-md flex flex-col md:flex-row bg-gray-100 dark:bg-neutral-800 w-full flex-1 max-w-7xl mx-auto border border-neutral-200 dark:border-neutral-700 overflow-hidden",
        "min-h-screen" // Changed from h-screen to min-h-screen
      )}
    >
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {open ? <Logo /> : <LogoIcon />}
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <SidebarLink key={idx} link={link} />
              ))}
            </div>
          </div>
          <div>
            <SidebarLink
              link={{
                label: "Manager",
                href: "#",
                icon: (
                  <Image
                    src="https://assets.aceternity.com/manu.png"
                    className="h-7 w-7 flex-shrink-0 rounded-full"
                    width={50}
                    height={50}
                    alt="Avatar"
                  />
                ),
              }}
            />
          </div>
        </SidebarBody>
      </Sidebar>
      <Dashboard />
    </div>
  );
}

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [tab, setTab] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5; // Changed from 10 to 5

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:3000/api/db/manager", {
        method: "GET",
      });
      const result = await res.json();
      const sortedData = result.sort((a: any, b: any) => b.fraudScore - a.fraudScore);
      setData(sortedData);
    };

    fetchData();
  }, []);

  // Calculate statistics
  const totalApprovedExpenditures = data
    .filter((exp: any) => exp.status === "Approved")
    .reduce((acc: number, exp: any) => acc + exp.amount, 0);
  const approvedRequests = data.filter((exp: any) => exp.status === "Approved").length;
  const pendingRequests = data.filter((exp: any) => exp.status === "Pending").length;
  const declinedRequests = data.filter((exp: any) => exp.status === "Declined").length;

  // Filter expenses based on active tab
  const filteredExpenses = tab === "all" ? data : data.filter((exp: any) => exp.status.toLowerCase() === tab);

  // Pagination calculations
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedExpenses = filteredExpenses.slice(startIndex, endIndex);
  const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage);

  return (
    <div className="flex flex-1 overflow-auto">
      {" "}
      {/* Added overflow-auto */}
      <div className="p-4 rounded-tl-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 flex flex-col gap-4 flex-1 w-full overflow-y-auto">
        {/* Added overflow-y-auto */}
        <h1 className="text-4xl font-semibold">Manager Dashboard</h1>
        {/* New stats cards */}
        <div className="grid gap-4 grid-cols-1 md:grid-cols-4">
          <Card>
            <CardContent>
              <h2 className="text-lg font-medium my-4 mx-2">Total Approved Expenditures</h2>
              <p className="text-2xl font-bold my-2 mx-2">{"₹" + totalApprovedExpenditures.toFixed(2)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <h2 className="text-lg font-medium my-4 mx-2">Approved Requests</h2>
              <p className="text-2xl font-bold m-2">{approvedRequests}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <h2 className="text-lg font-medium my-4 mx-2">Pending Requests</h2>
              <p className="text-2xl font-bold m-2">{pendingRequests}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <h2 className="text-lg font-medium my-4 mx-2">Declined Requests</h2>
              <p className="text-2xl font-bold m-2">{declinedRequests}</p>
            </CardContent>
          </Card>
        </div>
        {/* Updated Tabs with improved styling */}
        <Tabs className="" value={tab} onValueChange={setTab} defaultValue="all">
          <TabsList className="w-full flex justify-between border-b border-gray-200 dark:border-neutral-700">
            <TabsTrigger
              className="m-2 px-4 py-2 rounded-full transition-colors hover:bg-gray-200 dark:hover:bg-neutral-700 data-[state=active]:bg-[#F866AB] data-[state=active]:text-white"
              value="all"
            >
              All
            </TabsTrigger>
            <TabsTrigger
              className="m-2 px-4 py-2 rounded-full transition-colors hover:bg-gray-200 dark:hover:bg-neutral-700 data-[state=active]:bg-[#F866AB] data-[state=active]:text-white"
              value="approved"
            >
              Approved
            </TabsTrigger>
            <TabsTrigger
              className="m-2 px-4 py-2 rounded-full transition-colors hover:bg-gray-200 dark:hover:bg-neutral-700 data-[state=active]:bg-[#F866AB] data-[state=active]:text-white"
              value="pending"
            >
              Pending
            </TabsTrigger>
            <TabsTrigger
              className="m-2 px-4 py-2 rounded-full transition-colors hover:bg-gray-200 dark:hover:bg-neutral-700 data-[state=active]:bg-[#F866AB] data-[state=active]:text-white"
              value="declined"
            >
              Declined
            </TabsTrigger>
          </TabsList>
        </Tabs>
        {/* Existing Expense List using filtered data */}
        <Card>
          <CardContent>
            <ExpenseList2 expenses={paginatedExpenses} showEmployeeId={true} linkPrefix="/manager/expense" />

            {/* Pagination Controls */}
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Showing {startIndex + 1} to {Math.min(endIndex, filteredExpenses.length)} of {filteredExpenses.length}{" "}
                entries
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  <IconChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <IconChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export const Logo = () => {
  return (
    <Link href="#" className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20">
      <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-medium text-black dark:text-white whitespace-pre"
      >
        OutofBounds
      </motion.span>
    </Link>
  );
};

export const LogoIcon = () => {
  return (
    <Link href="#" className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20">
      <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
    </Link>
  );
};
