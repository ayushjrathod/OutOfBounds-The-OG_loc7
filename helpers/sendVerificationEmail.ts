import VerificationEmail from "@/emails/verificationEmail";
import { resend } from "@/lib/resend";
import { ApiResponse } from "@/types/ApiResponse";

export async function sendVerificationEmail(email: string, username: string, verifyCode: string): Promise<ApiResponse> {
  try {
    await resend.emails.send({
      from: "onboarding@resend.dev",
      to: email,
      subject: "AnonFeed Verification Code",
      react: VerificationEmail({ username, otp: verifyCode }),
    });
    return { success: true, message: "verification mail send sucessfully" };
  } catch (err) {
    console.error("error sending verification mail", err);
    return { success: false, message: "failed to send verifcation email" };
  }
}
