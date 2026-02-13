import { Heading, Text, Section, Button } from "@react-email/components";
import { Layout, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface EmailVerificationEmailProps {
  branding: Branding;
  verification_link: string;
  user_name?: string;
  expiry_time?: string;
}

export const EmailVerificationEmail = ({
  branding,
  verification_link,
  user_name,
  expiry_time = "24 hours",
}: EmailVerificationEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[22px] font-medium"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        {user_name ? `Hello ${toTitleCase(user_name)},` : "Verify your email"}
      </Heading>

      <Text
        className="text-sm leading-6"
        style={{ color: branding.text_color }}
      >
        Click the button below to verify your email.
      </Text>

      <Section className="my-8">
        <Button
          className="box-border w-full rounded-[6px] px-[12px] py-[12px] text-center font-medium text-white text-[16px]"
          style={{ backgroundColor: branding.primary_color }}
          href={verification_link}
        >
          Verify Email
        </Button>
      </Section>

      <Text
        className="text-xs leading-6"
        style={{ color: branding.tertiary_color }}
      >
        This link will expire in {expiry_time}.
        <br /><br />
        If you didn't create an account, you can safely ignore this email.
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function EmailVerificationEmailPreview() {
  return (
    <EmailVerificationEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      verification_link="https://example.com/verify?token=abc123"
      user_name="John"
    />
  );
}
