import { Heading, Text, Section, Button } from "@react-email/components";
import { Layout, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface WelcomeEmailProps {
  branding: Branding;
  user_name?: string;
  login_link?: string;
  custom_message?: string;
}

export const WelcomeEmail = ({
  branding,
  user_name,
  login_link,
  custom_message,
}: WelcomeEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Your account is ready{user_name ? `, ${toTitleCase(user_name)}` : ""}!
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        {custom_message || "Log in to access company resources."}
      </Text>

      {login_link && (
        <Section className="my-8">
          <Button
            className="email-button box-border w-full rounded-[6px] px-[12px] py-[12px] text-center font-medium text-[16px]"
            style={{ backgroundColor: branding.primary_color, color: branding.button_text_color || "#ffffff" }}
            href={login_link}
          >
            Log In
          </Button>
        </Section>
      )}
    </Layout>
  );
};

// Preview with sample data
export default function WelcomeEmailPreview() {
  return (
    <WelcomeEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      user_name="John"
      login_link="https://example.com/login"
    />
  );
}
