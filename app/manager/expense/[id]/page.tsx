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
          setImgSrc(data.receiptImage || "/placeholder.svg");
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "Approved" }),
      });

      if (res.ok) {
        setStatus("Approved");
        toast({
          title: "Expense Approved",
          description: `Expense ${params.id} has been approved successfully.`,
          variant: "default",
        });
      } else throw new Error("Failed to approve expense");
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "Declined", reason: rejectionReason }),
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
      } else throw new Error("Failed to decline expense");
    } catch (error) {
      console.error("Failed to decline:", error);
      toast({
        title: "Error",
        description: "Failed to decline expense. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.25, 0.5));

  const handleMouseDown = (e: MouseEvent) => {
    if (zoomLevel > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging && zoomLevel > 1) {
      setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  useEffect(() => {
    setPosition({ x: 0, y: 0 });
  }, [zoomLevel, isImageOpen]);

  if (loading) return <div className="p-4 text-gray-600">Loading...</div>;
  if (!expense) return <div className="p-4 text-red-600">Expense not found.</div>;

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <Card className="shadow-lg">
        <CardHeader className="border-b">
          <CardTitle className="text-2xl font-bold text-gray-800 flex items-center justify-between">
            <span>Expense Details - #{params.id}</span>
            <Badge
              variant={status === "Approved" ? "default" : status === "Declined" ? "destructive" : "secondary"}
              className="text-sm py-1 px-3"
            >
              {status}
            </Badge>
          </CardTitle>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <DetailItem label="Expense Type" value={expense.expenseType} />
              <DetailItem label="Amount" value={`₹${expense.amount.toFixed(2)}`} />
              <DetailItem label="Date" value={new Date(expense.date).toLocaleDateString()} />
              <DetailItem label="Vendor" value={expense.vendor} />
            </div>

            <Dialog open={isImageOpen} onOpenChange={setIsImageOpen}>
              <DialogTrigger asChild>
                <div className="relative aspect-square cursor-pointer group">
                  <Image
                    src={imgSrc}
                    alt="Receipt"
                    fill
                    className="object-cover rounded-lg border transition-transform group-hover:scale-105"
                    onError={() => setImgSrc("/placeholder.svg")}
                  />
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-lg">
                    <span className="text-white font-medium">View Receipt</span>
                  </div>
                </div>
              </DialogTrigger>
              <DialogContent className="max-w-4xl h-[80vh] p-0 overflow-hidden">
                <div
                  className="relative w-full h-full overflow-hidden"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={() => setIsDragging(false)}
                  onMouseLeave={() => setIsDragging(false)}
                >
                  <div
                    className="relative w-full h-full transition-transform duration-200"
                    style={{
                      transform: `scale(${zoomLevel}) translate(${position.x / zoomLevel}px, ${position.y / zoomLevel}px)`,
                      cursor: isDragging ? "grabbing" : zoomLevel > 1 ? "grab" : "default",
                    }}
                  >
                    <Image
                      src={imgSrc}
                      alt="Receipt"
                      fill
                      className="object-contain"
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
          </div>

          <Section title="Description">
            <p className="text-gray-600 leading-relaxed">{expense.description}</p>
          </Section>

          <Section title="Item Details">
            <div className="space-y-2">
              {expense.item_details.map((item: any, index: number) => (
                <div key={index} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
                  <span className="font-medium text-gray-700">{item.item}</span>
                  <span className="text-gray-600">
                    ₹{(typeof item.amount !== "string" ? parseFloat(item.amount) : item.amount).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="AI Analysis">
            <AlertBanner
              icon={
                expense.fraudScore > 0.5 || expense.isAnomaly ? (
                  <AlertTriangle className="w-5 h-5" />
                ) : (
                  <CheckCircle className="w-5 h-5" />
                )
              }
              message={
                expense.fraudScore > 0.5 || expense.isAnomaly
                  ? "This expense has been flagged for review."
                  : "This expense appears to be normal."
              }
              color={expense.fraudScore > 0.5 || expense.isAnomaly ? "yellow" : "green"}
            />
            <div className="mt-2 text-sm text-gray-500">
              <p>{expense.aiSummary}</p>
            </div>
          </Section>

          <Section title="Submission Details">
            <DetailItem label="Submitted Date" value={new Date(expense.submittedDate).toLocaleDateString()} />
          </Section>
        </CardContent>

        <CardFooter className="border-t px-6 py-4 bg-gray-50">
          <div className="flex justify-end space-x-3 w-full">
            <Button
              variant="outline"
              onClick={() => router.push("/manager")}
              className="border-gray-300 text-gray-700 hover:bg-gray-100"
            >
              Back to List
            </Button>

            <Dialog open={isDeclineDialogOpen} onOpenChange={setIsDeclineDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive" disabled={status !== "Pending"} className="shadow-sm">
                  Decline
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Decline Expense</DialogTitle>
                </DialogHeader>
                <div className="py-4 space-y-3">
                  <label htmlFor="reason" className="block text-sm font-medium text-gray-700">
                    Reason for declining
                  </label>
                  <Input
                    id="reason"
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Enter reason for declining"
                    className="focus-visible:ring-2 focus-visible:ring-blue-500"
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

            <Button
              variant="default"
              onClick={handleApprove}
              disabled={status !== "Pending"}
              className="bg-green-600 hover:bg-green-700 shadow-sm text-white"
            >
              Approve
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}

// Helper Components
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      {children}
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b">
      <span className="text-gray-600 font-medium">{label}</span>
      <span className="text-gray-800">{value}</span>
    </div>
  );
}

function AlertBanner({ icon, message, color }: { icon: React.ReactNode; message: string; color: "yellow" | "green" }) {
  const colorClasses = {
    yellow: "bg-yellow-50 text-yellow-700",
    green: "bg-green-50 text-green-700",
  };

  return (
    <div className={`${colorClasses[color]} p-4 rounded-lg flex items-center space-x-3`}>
      {icon}
      <span className="font-medium">{message}</span>
    </div>
  );
}
