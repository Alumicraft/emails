import { Heading, Section } from "@react-email/components";
import { Layout } from "./shared";
import type { Branding } from "./shared";

export type { Branding } from "./shared";

export interface NotificationEmailProps {
  branding: Branding;
  title: string;
  message: string;
}

export const NotificationEmail = ({ branding, title, message }: NotificationEmailProps) => (
  <Layout branding={branding}>
    <Heading
      className="email-heading"
      style={{ color: branding.text_color, marginTop: 0, fontSize: "24px", fontWeight: 500, lineHeight: "32px" }}
    >
      {title}
    </Heading>
    <Section>
      <div
        className="email-text"
        style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
        dangerouslySetInnerHTML={{ __html: message }}
      />
    </Section>
  </Layout>
);

export default function NotificationEmailPreview() {
  return (
    <NotificationEmail
      branding={{ company: "DCR", primary_color: "#000000", text_color: "#1f1f1f", background_color: "#ffffff", font_family: "Arial, sans-serif" }}
      title="Your request has been updated"
      message={'<p>HBR-TEST is ready for review.</p><p><a href="https://example.com/portal">Open request</a></p>'}
    />
  );
}
