import {
  Html,
  Head,
  Body,
  Container,
  Section,
  Img,
  Text,
  Link,
  Preview,
  Button as EmailButton,
  Row,
  Column,
  Hr,
  Tailwind,
} from "@react-email/components";
import * as React from "react";
import tailwindConfig from "../tailwind.config";

// ============================================================================
// HELPERS
// ============================================================================

export const toTitleCase = (str?: string): string => {
  if (!str) return "";
  return str
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

// ============================================================================
// INTERFACES
// ============================================================================

export interface Branding {
  company: string;
  logo_url?: string;
  logo_url_dark?: string;
  logo_url_secondary?: string;
  logo_url_secondary_dark?: string;
  logo_height?: number;
  logo_alt?: string;
  background_image_url?: string;
  primary_color: string;
  secondary_color?: string;
  tertiary_color?: string;
  text_color: string;
  background_color: string;
  card_color?: string;
  table_color?: string;
  border_color?: string;
  amount_bg_color?: string;
  amount_text_color?: string;
  button_text_color?: string;
  primary_color_dark?: string;
  card_color_dark?: string;
  table_color_dark?: string;
  border_color_dark?: string;
  amount_bg_color_dark?: string;
  amount_text_color_dark?: string;
  secondary_color_dark?: string;
  tertiary_color_dark?: string;
  text_color_dark?: string;
  background_color_dark?: string;
  button_text_color_dark?: string;
  font_family: string;
  footer_text?: string;
  preheader?: string;
  website_url?: string;
  company_email?: string;
  company_phone?: string;
  mailing_address?: string;
}

export interface Item {
  item_name: string;
  qty: number;
  rate?: string;
  amount?: string;
}

// ============================================================================
// BUTTON COMPONENT
// ============================================================================

export const Button = ({ href, color, textColor, children }: { href: string; color: string; textColor?: string; children: React.ReactNode }) => (
  <EmailButton
    href={href}
    className="email-button"
    style={{
      backgroundColor: color,
      color: textColor || "#ffffff",
      display: "inline-block",
      padding: "12px 24px",
      borderRadius: "4px",
      fontWeight: 400,
      textDecoration: "none",
      border: "none",
    }}
  >
    {children}
  </EmailButton>
);

// ============================================================================
// LOGO COMPONENT (dark mode swap via CSS show/hide)
// ============================================================================

export const Logo = ({
  lightSrc,
  darkSrc,
  alt,
  height,
  className,
}: {
  lightSrc: string;
  darkSrc?: string;
  alt: string;
  height: string | number;
  className?: string;
}) => {
  if (!darkSrc) {
    return <Img src={lightSrc} height={height} alt={alt} className={className} />;
  }
  return (
    <>
      <Img src={lightSrc} height={height} alt={alt} className={`email-logo-light ${className || ""}`} />
      <Img src={darkSrc} height={height} alt="" className={`email-logo-dark ${className || ""}`} style={{ display: "none", maxHeight: 0, overflow: "hidden" }} />
    </>
  );
};

// ============================================================================
// FOOTER COMPONENT
// ============================================================================

export const Footer = ({ branding }: { branding: Branding }) => {
  const footerLogo = branding.logo_url_secondary || branding.logo_url;
  const footerLogoDark = branding.logo_url_secondary_dark || branding.logo_url_dark;
  const tertiaryColor = branding.tertiary_color || "#6b7280";

  return (
    <Section className="mt-12 mb-8">
      {/* Divider line */}
      <Hr className="email-footer-divider mb-8" style={{ border: "none", borderTop: `1px solid ${tertiaryColor}`, marginTop: 0 }} />
      {/* Logo */}
      {footerLogo && (
        <Logo
          lightSrc={footerLogo}
          darkSrc={footerLogoDark}
          alt={branding.logo_alt || branding.company}
          height="24"
          className="mb-6"
        />
      )}

      {/* Contact */}
      {(branding.company_email || branding.company_phone) && (
        <Text className="email-footer-text" style={{ margin: "0 0 8px 0", fontSize: "14px", color: tertiaryColor, lineHeight: "20px" }}>
          {branding.company_email && (
            <Link
              href={`mailto:${branding.company_email}`}
              className="email-footer-link"
              style={{ color: tertiaryColor, textDecoration: "none" }}
            >
              {branding.company_email}
            </Link>
          )}
          {branding.company_email && branding.company_phone && " | "}
          {branding.company_phone && (
            <Link
              href={`tel:${branding.company_phone.replace(/[^+\d]/g, "")}`}
              className="email-footer-link"
              style={{ color: tertiaryColor, textDecoration: "none" }}
            >
              {branding.company_phone}
            </Link>
          )}
        </Text>
      )}

      {/* Address */}
      {branding.mailing_address && (
        <Text className="email-footer-text" style={{ margin: "0", fontSize: "14px", color: tertiaryColor, lineHeight: "20px" }}>
          <Link
            href={`https://maps.google.com/?q=${encodeURIComponent(branding.mailing_address)}`}
            className="email-footer-link"
            style={{ color: tertiaryColor, textDecoration: "none" }}
          >
            {branding.mailing_address}
          </Link>
        </Text>
      )}
    </Section>
  );
};

// ============================================================================
// CONFIDENTIALITY COMPONENT
// ============================================================================

export const Confidentiality = () => (
  <Text className="email-confidentiality" style={{
    fontSize: "11px",
    lineHeight: "16px",
    color: "#9ca3af",
    textAlign: "center",
    margin: "24px 0 0 0",
  }}>
    This email and any attachments are confidential and intended solely for the recipient. If you received this in error, please delete it and notify the sender.
  </Text>
);

// ============================================================================
// LAYOUT COMPONENT
// ============================================================================

export const Layout = ({
  branding,
  preview,
  children,
}: {
  branding: Branding;
  preview?: string;
  children: React.ReactNode;
}) => {
  const darkBg = branding.background_color_dark || "#1a1a1a";
  const darkCard = branding.card_color_dark || "#000000";
  const darkTable = branding.table_color_dark || darkBg;
  const darkBorder = branding.border_color_dark || "#4b5563";
  const darkHighlight = branding.amount_bg_color_dark || "#374151";
  const darkText = branding.text_color_dark || "#ffffff";
  const buttonTextColorDark = branding.button_text_color_dark || branding.button_text_color || "#ffffff";
  const tertiaryColorDark = branding.tertiary_color_dark || "#9ca3af";

  const darkModeStyles = `
    @media (prefers-color-scheme: dark) {
      .email-body { background-color: ${darkBg} !important; }
      .email-card { background-color: ${darkCard} !important; }
      .email-heading, .email-text { color: ${darkText} !important; }
      .email-row-label { color: #e5e7eb !important; }
      .email-row-value { color: #d1d5db !important; }
      .email-divider { border-color: ${darkBorder} !important; }
      .email-confidentiality { color: #6b7280 !important; }
      .email-button { color: ${buttonTextColorDark} !important; }
      .email-logo-light { display: none !important; }
      .email-logo-dark { display: block !important; max-height: none !important; overflow: visible !important; }
      .email-footer-text { color: ${tertiaryColorDark} !important; }
      .email-footer-link { color: ${tertiaryColorDark} !important; }
      .email-footer-divider { border-color: ${darkBorder} !important; }
      .email-info-card { background-color: ${darkTable} !important; }
      .email-amount-bg { background-color: ${darkHighlight} !important; }
    }
    @media screen {
      u ~ div .email-logo-dark { display: none !important; max-height: 0 !important; overflow: hidden !important; }
    }
    @media screen and (prefers-color-scheme: dark) {
      u ~ div .email-logo-light { display: none !important; }
      u ~ div .email-logo-dark { display: block !important; max-height: none !important; overflow: visible !important; }
    }
  `;

  return (
    <Html lang="en">
      <Head>
        <meta name="color-scheme" content="light dark" />
        <meta name="supported-color-schemes" content="light dark" />
        <style dangerouslySetInnerHTML={{ __html: darkModeStyles }} />
      </Head>
      {preview && <Preview>{preview}</Preview>}
      <Tailwind config={tailwindConfig}>
        <Body
          className="mx-auto my-0 font-sans email-body"
          style={{
            fontFamily: branding.font_family,
            backgroundColor: branding.background_color,
          }}
        >
          <Container className="mx-auto my-0 pt-6 pb-8 max-w-[600px]">
            <Section
              className="px-6 py-8 email-card"
              style={{
                backgroundColor: branding.card_color || "#ffffff",
              }}
            >
              {branding.logo_url && (
                <Logo
                  lightSrc={branding.logo_url}
                  darkSrc={branding.logo_url_dark}
                  alt={branding.logo_alt || branding.company}
                  height={branding.logo_height || 48}
                  className="mt-4 mb-8"
                />
              )}

              {children}

              <Footer branding={branding} />
            </Section>
            <Confidentiality />
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

// ============================================================================
// INFO CARD COMPONENTS
// ============================================================================

const monoFont = "Courier, monospace";

export const InfoCard = ({ branding, children }: { branding: Branding; children: React.ReactNode }) => (
  <table cellPadding="0" cellSpacing="0" className="email-info-card" style={{
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "32px",
    marginBottom: "32px",
    backgroundColor: branding.table_color || branding.background_color,
    borderRadius: "4px",
    overflow: "hidden",
  }}>
    <tbody>
      {children}
    </tbody>
  </table>
);

export const InfoRow = ({ branding, label, value, valueColor }: { branding: Branding; label: string; value: string; valueColor?: string }) => (
  <tr>
    <td className="email-row-label email-divider" style={{
      padding: "12px 16px",
      borderBottom: `1px solid ${branding.border_color || "#e5e7eb"}`,
      color: branding.secondary_color || "#6b7280",
      fontSize: "14px",
      fontWeight: 400,
      whiteSpace: "nowrap",
    }}>{label}</td>
    <td className="email-row-value email-divider" style={{
      padding: "12px 16px",
      borderBottom: `1px solid ${branding.border_color || "#e5e7eb"}`,
      color: valueColor || branding.secondary_color || "#1f2937",
      fontSize: "14px",
      fontFamily: monoFont,
      textAlign: "right",
    }}>{value}</td>
  </tr>
);

export const InfoAmount = ({ branding, label, value }: { branding: Branding; label: string; value: string }) => (
  <tr>
    <td className="email-row-label email-amount-bg" style={{
      padding: "12px 16px",
      color: branding.secondary_color || "#6b7280",
      fontSize: "14px",
      fontWeight: 400,
      whiteSpace: "nowrap",
      backgroundColor: branding.amount_bg_color || "#e5e7eb",
    }}>{label}</td>
    <td className="email-row-value email-amount-bg" style={{
      padding: "12px 16px",
      color: branding.amount_text_color || branding.text_color || "#000000",
      fontSize: "14px",
      fontFamily: monoFont,
      fontWeight: 700,
      textAlign: "right",
      backgroundColor: branding.amount_bg_color || "#e5e7eb",
    }}>{value}</td>
  </tr>
);
