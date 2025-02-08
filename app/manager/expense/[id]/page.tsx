"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { AlertTriangle, CheckCircle, ZoomIn, ZoomOut } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { MouseEvent, useEffect, useState } from "react";

export default function ExpenseDetails({ params }: { params: { id: string } }) {
  const [expense, setExpense] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Pending");
  const [imgSrc, setImgSrc] = useState("");
  const [isImageOpen, setIsImageOpen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [rejectionReason, setRejectionReason] = useState("");
  const [isDeclineDialogOpen, setIsDeclineDialogOpen] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    async function fetchExpense() {
      try {
        const res = await fetch(`/api/db/manager/expenses?id=${params.id}`);
        const data = await res.json();
        setExpense(data);
        if (data) {
          setStatus(data.status);
          // Update to use Cloudinary URL directly
          if (data.receiptImage) {
            setImgSrc(data.receiptImage);
          } else {
            setImgSrc("/placeholder.svg");
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchExpense();
  }, [params.id]);

  const handleApprove = async () => {
    try {
      const res = await fetch(`/api/db/manager/expenses?id=${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: "Approved" }),
      });

      if (res.ok) {
        setStatus("Approved");
        toast({
          title: "Expense Approved",
          description: `Expense ${params.id} has been approved successfully.`,
          variant: "default",
        });
      } else {
        throw new Error("Failed to approve expense");
      }
    } catch (error) {
      console.error("Failed to approve:", error);
      toast({
        title: "Error",
        description: "Failed to approve expense. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleDecline = async () => {
    if (!rejectionReason.trim()) {
      toast({
        title: "Error",
        description: "Please provide a reason for declining the expense.",
        variant: "destructive",
      });
      return;
    }

    try {
      const res = await fetch(`/api/db/manager/expenses?id=${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: "Declined",
          reason: rejectionReason,
        }),
      });

      if (res.ok) {
        setStatus("Declined");
        setIsDeclineDialogOpen(false);
        setRejectionReason("");
        toast({
          title: "Expense Declined",
          description: `Expense ${params.id} has been declined.`,
          variant: "default",
        });
      } else {
        throw new Error("Failed to decline expense");
      }
    } catch (error) {
      console.error("Failed to decline:", error);
      toast({
        title: "Error",
        description: "Failed to decline expense. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 0.25, 3)); // Max zoom 3x
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev - 0.25, 0.5)); // Min zoom 0.5x
  };

  const handleMouseDown = (e: MouseEvent) => {
    if (zoomLevel > 1) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y,
      });
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging && zoomLevel > 1) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Reset position when zoom level changes or dialog closes
  useEffect(() => {
    setPosition({ x: 0, y: 0 });
  }, [zoomLevel, isImageOpen]);

  if (loading) return <div>Loading...</div>;
  if (!expense) return <div>Expense not found.</div>;

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Expense Details - {params.id}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Dialog open={isImageOpen} onOpenChange={setIsImageOpen}>
            <DialogTrigger asChild>
              <div className="aspect-video relative cursor-pointer">
                <Image
                  src={imgSrc}
                  alt="Receipt"
                  layout="fill"
                  objectFit="contain"
                  onError={() => setImgSrc("/placeholder.svg")}
                />
              </div>
            </DialogTrigger>
            <DialogContent className="max-w-4xl h-[80vh]">
              <div
                className="relative w-full h-full overflow-hidden"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
              >
                <div
                  className="relative w-full h-full transition-transform duration-200"
                  style={{
                    transform: `scale(${zoomLevel}) translate(${position.x / zoomLevel}px, ${position.y / zoomLevel}px)`,
                    cursor: zoomLevel > 1 ? "grab" : "default",
                    cursor: isDragging ? "grabbing" : undefined,
                  }}
                >
                  <Image
                    src={imgSrc}
                    alt="Receipt"
                    layout="fill"
                    objectFit="contain"
                    onError={() => setImgSrc("/placeholder.svg")}
                    draggable={false}
                  />
                </div>
                <div className="absolute bottom-4 right-4 flex gap-2">
                  <Button variant="secondary" size="icon" onClick={handleZoomOut} disabled={zoomLevel <= 0.5}>
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <Button variant="secondary" size="icon" onClick={handleZoomIn} disabled={zoomLevel >= 3}>
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold">Expense Type</h3>
              <p>{expense.expenseType}</p>
            </div>
            <div>
              <h3 className="font-semibold">Amount</h3>
              <p> ₹{expense.amount.toFixed(2)}</p>
            </div>
            <div>
              <h3 className="font-semibold">Date</h3>
              <p>{new Date(expense.date).toLocaleDateString()}</p>
            </div>
            <div>
              <h3 className="font-semibold">Vendor</h3>
              <p>{expense.vendor}</p>
            </div>
            <div className="col-span-2">
              <h3 className="font-semibold">Description</h3>
              <p>{expense.description}</p>
            </div>
          </div>
          <div>
            <h3 className="font-semibold">Item Details</h3>
            <ul>
              {expense.item_details.map((item: any, index: number) => (
                <li key={index}>
                  {item.item}: ${(typeof item.amount != "string" ? parseFloat(item.amount) : item.amount).toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold">AI Summary</h3>
            <p>{expense.aiSummary}</p>
          </div>
          <div>
            <h3 className="font-semibold">Status</h3>
            <Badge variant={status === "Approved" ? "default" : status === "Declined" ? "destructive" : "secondary"}>
              {status}
            </Badge>
          </div>
          <div>
            <h3 className="font-semibold">Submitted Date</h3>
            <p>{new Date(expense.submittedDate).toLocaleDateString()}</p>
          </div>
          {expense.fraudScore > 0.5 || expense.isAnomaly ? (
            <div className="bg-yellow-100 p-4 rounded-md flex items-center space-x-2">
              <AlertTriangle className="text-yellow-700" />
              <span className="text-yellow-700">This expense has been flagged for review.</span>
            </div>
          ) : (
            <div className="bg-green-100 p-4 rounded-md flex items-center space-x-2">
              <CheckCircle className="text-green-700" />
              <span className="text-green-700">This expense appears to be normal.</span>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
          <Button variant="outline" onClick={() => router.push("/manager")}>
            Back
          </Button>
          <Dialog open={isDeclineDialogOpen} onOpenChange={setIsDeclineDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="destructive" disabled={status !== "Pending"}>
                Decline
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Decline Expense</DialogTitle>
              </DialogHeader>
              <div className="py-4">
                <label htmlFor="reason" className="block text-sm font-medium mb-2">
                  Reason for declining
                </label>
                <Input
                  id="reason"
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="Enter reason for declining"
                />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDeclineDialogOpen(false)}>
                  Cancel
                </Button>
                <Button variant="destructive" onClick={handleDecline}>
                  Confirm Decline
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Button variant="default" onClick={handleApprove} disabled={status !== "Pending"}>
            Approve
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
