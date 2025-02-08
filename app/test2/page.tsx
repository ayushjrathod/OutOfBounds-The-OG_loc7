"use client";

import { MetricsCard } from "@/components/metrics-card";
import { BookingsTable } from "@/components/bookings-table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Calendar,
  Home,
  MessageSquare,
  Bell,
  BarChart2,
  CreditCard,
  Star,
  HelpCircle,
  Globe,
  Heart,
  Menu,
} from "lucide-react";
import { useState } from "react";

// Sample data - replace with your actual data fetching logic
const metrics = [
  { title: "Revenue", value: "$3,563.00", change: { value: 16, label: "last month" } },
  { title: "Bookings", value: "126", change: { value: 34, label: "last month" } },
  { title: "Applications", value: "87", change: { value: 28, label: "last month" } },
  { title: "Ratings", value: "4.5", subtitle: "Average rating" },
];

const bookings = [
  {
    id: "3849",
    customer: {
      name: "Albert Flores",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Albert",
      guests: 1,
    },
    checkIn: "Sep 12, 2 PM",
    checkOut: "Sep 14, 12 PM",
    booked: {
      date: "Aug 4, 2024",
      time: "12:24 PM",
    },
    totalPayout: 115.5,
    status: "pending" as const,
  },
  // Add more sample bookings...
];

const navigation = [
  { label: "Dashboard", icon: <Home className="h-5 w-5" />, href: "#" },
  { label: "Bookings", icon: <Calendar className="h-5 w-5" />, href: "#" },
  { label: "Messages", icon: <MessageSquare className="h-5 w-5" />, href: "#" },
  { label: "Notifications", icon: <Bell className="h-5 w-5" />, href: "#" },
  { label: "Analytics", icon: <BarChart2 className="h-5 w-5" />, href: "#" },
  { label: "Payments", icon: <CreditCard className="h-5 w-5" />, href: "#" },
  { label: "Reviews", icon: <Star className="h-5 w-5" />, href: "#" },
  { label: "Help", icon: <HelpCircle className="h-5 w-5" />, href: "#" },
];

export default function DashboardPage() {
  const [open, setOpen] = useState(true);

  return (
    <div className="flex min-h-screen">
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody>
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-2 text-xl font-semibold mb-8">
              <div className="h-8 w-8 rounded-lg bg-pink-500" />
              <span>StayWise</span>
            </div>

            <div className="flex-1">
              {navigation.map((item) => (
                <SidebarLink key={item.label} link={item} />
              ))}
            </div>

            <div className="mt-auto">
              <div className="flex items-center gap-2">
                <Avatar>
                  <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=Jane" />
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="font-medium">Jane Doe</div>
                  <div className="text-xs text-neutral-500">Admin</div>
                </div>
              </div>
            </div>
          </div>
        </SidebarBody>
      </Sidebar>

      <main className="flex-1">
        <div className="flex h-16 items-center justify-between gap-4 border-b px-4">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
            <Input placeholder="Search bookings..." className="w-[300px] bg-neutral-50" />
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <Globe className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Heart className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold">Bookings</h1>
          </div>

          <div className="mb-8 grid gap-4 md:grid-cols-4">
            {metrics.map((metric) => (
              <MetricsCard key={metric.title} {...metric} />
            ))}
          </div>

          <Tabs defaultValue="all" className="w-full">
            <TabsList>
              <TabsTrigger value="all">All (6)</TabsTrigger>
              <TabsTrigger value="pending">Pending (2)</TabsTrigger>
              <TabsTrigger value="active">Active (2)</TabsTrigger>
              <TabsTrigger value="completed">Completed (2)</TabsTrigger>
            </TabsList>
            <TabsContent value="all" className="mt-4">
              <BookingsTable bookings={bookings} />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}
