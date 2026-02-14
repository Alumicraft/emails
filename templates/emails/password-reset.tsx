import { Heading, Text, Section, Button } from "@react-email/components";
import { Layout, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface PasswordResetEmailProps {
  branding: Branding;
  reset_link: string;
  user_name?: string;
  expiry_time?: string;
}

export const PasswordResetEmail = ({
  branding,
  reset_link,
  user_name,
  expiry_time = "1 hour",
}: PasswordResetEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        {user_name ? `Hello ${toTitleCase(user_name)},` : "Reset your password"}
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Click the button below to reset your password.
      </Text>

      <Section className="my-8">
        <Button
          className="email-button box-border w-full rounded-[6px] px-[12px] py-[12px] text-center font-medium text-[16px]"
          style={{ backgroundColor: branding.primary_color, color: branding.button_text_color || "#ffffff" }}
          href={reset_link}
        >
          Reset Password
        </Button>
      </Section>

      <Text
        className="text-xs leading-6"
        style={{ color: branding.tertiary_color }}
      >
        This link will expire in {expiry_time}.
        <br /><br />
        If you didn't request a password reset, you can safely ignore this email.
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function PasswordResetEmailPreview() {
  return (
    <PasswordResetEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      reset_link="https://example.com/reset?token=abc123"
      user_name="John"
      expiry_time="1 hour"
    />
  );
}
