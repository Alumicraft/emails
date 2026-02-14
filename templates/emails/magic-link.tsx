import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Img,
  Preview,
  Section,
  Tailwind,
  Text,
} from "@react-email/components";
import tailwindConfig from "../tailwind.config";
import { Footer, Confidentiality, Branding, toTitleCase } from "./shared";

export interface MagicLinkEmailProps {
  branding: Branding;
  magic_link: string;
  user_name?: string;
  expiry_time?: string;
}

export const MagicLinkEmail = ({
  branding,
  magic_link,
  user_name,
  expiry_time = "15 minutes",
}: MagicLinkEmailProps) => {
  return (
    <Html lang="en">
      <Head />
      <Preview>Sign in to {branding.company} with this magic link</Preview>
      <Tailwind config={tailwindConfig}>
        <Body
          className="mx-auto my-0 font-sans"
          style={{
            fontFamily: branding.font_family,
            backgroundColor: branding.background_color,
          }}
        >
          <Container
            className="mx-auto my-0 pt-5 px-6 pb-12 max-w-[600px]"
          >
            <Section
              className="mt-8 p-8"
              style={{
                backgroundColor: "#ffffff",
                borderRadius: "12px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                backgroundImage: branding.background_image_url
                  ? `linear-gradient(rgba(255,255,255,0.75), rgba(255,255,255,0.75)), url(${branding.background_image_url})`
                  : undefined,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }}
            >
              {branding.logo_url && (
                <Img
                  src={branding.logo_url}
                  height={branding.logo_height || 48}
                  alt={branding.logo_alt || branding.company}
                  className="mt-4 mb-8"
                />
              )}
              <Heading
                className="text-[24px] font-medium"
                style={{ color: branding.text_color }}
              >
                {user_name ? `Hello ${toTitleCase(user_name)}, sign in.` : "Sign in"}
              </Heading>
              <Text
                className="text-[15px] leading-6"
                style={{ color: branding.text_color }}
              >
                Click the button below to sign in.
              </Text>
              <Section className="my-8">
                <Button
                  className="box-border w-full rounded-[6px] px-[12px] py-[12px] text-center font-medium text-white text-[16px]"
                  style={{ backgroundColor: branding.primary_color }}
                  href={magic_link}
                >
                  Login
                </Button>
              </Section>
              <Text className="text-[12px]" style={{ color: branding.tertiary_color || "#6b7280" }}>
                This link will expire in {expiry_time}.
                <br /><br />
                If you didn't try to login, you can safely ignore this email.
              </Text>

              {/* Footer */}
              <Footer branding={branding} />
            </Section>
            <Confidentiality />
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

// Preview with sample data
export default function MagicLinkEmailPreview() {
  return (
    <MagicLinkEmail
      branding={{
        company: "Acme Inc",
        logo_url: "https://react-email-demo-ijnnx5hul-resend.vercel.app/static/vercel-logo.png",
        logo_url_secondary: "https://react-email-demo-ijnnx5hul-resend.vercel.app/static/vercel-logo.png",
        primary_color: "#4f46e5",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
        website_url: "https://acme.com",
        mailing_address: "123 Main Street, San Francisco, CA 94102",
        company_email: "hello@acme.com",
        company_phone: "+1 (555) 123-4567",
        instagram_url: "https://instagram.com/acme",
        tiktok_url: "https://tiktok.com/@acme",
        facebook_url: "https://facebook.com/acme",
        youtube_url: "https://youtube.com/acme",
        twitter_url: "https://twitter.com/acme",
      }}
      user_name="John"
      magic_link="https://acme.com/auth/verify?token=abc123xyz"
      expiry_time="15 minutes"
    />
  );
}
