import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { MoreHorizontal } from "lucide-react";

interface Booking {
  id: string;
  customer: {
    name: string;
    avatar: string;
    guests: number;
  };
  checkIn: string;
  checkOut: string;
  booked: {
    date: string;
    time: string;
  };
  totalPayout: number;
  status: "pending" | "upcoming" | "active";
}

export function BookingsTable({ bookings }: { bookings: Booking[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">#</TableHead>
          <TableHead>Customer</TableHead>
          <TableHead>Check-In</TableHead>
          <TableHead>Checkout</TableHead>
          <TableHead>Booked</TableHead>
          <TableHead className="text-right">Total Payout</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="w-[50px]"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {bookings.map((booking) => (
          <TableRow key={booking.id}>
            <TableCell className="text-neutral-500">#{booking.id}</TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatar.png" />
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium">{booking.customer.name}</div>
                  <div className="text-xs text-neutral-500">
                    {booking.customer.guests} guest{booking.customer.guests !== 1 ? "s" : ""}
                  </div>
                </div>
              </div>
            </TableCell>
            <TableCell>{booking.checkIn}</TableCell>
            <TableCell>{booking.checkOut}</TableCell>
            <TableCell>
              <div>
                <div>{booking.booked.date}</div>
                <div className="text-xs text-neutral-500">{booking.booked.time}</div>
              </div>
            </TableCell>
            <TableCell className="text-right">${booking.totalPayout.toFixed(2)}</TableCell>
            <TableCell>
              <Badge
                variant="secondary"
                className={
                  booking.status === "pending"
                    ? "bg-blue-50 text-blue-600"
                    : booking.status === "upcoming"
                      ? "bg-green-50 text-green-600"
                      : "bg-pink-50 text-pink-600"
                }
              >
                {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
              </Badge>
            </TableCell>
            <TableCell>
              <button className="rounded-md p-2 hover:bg-neutral-100">
                <MoreHorizontal className="h-4 w-4" />
              </button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
