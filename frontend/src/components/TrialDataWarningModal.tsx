import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";

const SALES_EMAIL = "contact@pricing-star.com";

interface TrialDataWarningModalProps {
  open: boolean;
  onDismiss: () => void;
}

export function TrialDataWarningModal({ open, onDismiss }: TrialDataWarningModalProps) {
  const handleContactSales = () => {
    window.location.href = `mailto:${SALES_EMAIL}?subject=Pricing Star — Production access`;
    onDismiss();
  };

  return (
    <Modal
      open={open}
      onClose={onDismiss}
      title="Données de production détectées"
      size="sm"
      footer={
        <>
          <Button variant="ghost" size="sm" onClick={onDismiss}>
            J&apos;utilise des données illustratives
          </Button>
          <Button variant="primary" size="sm" onClick={handleContactSales}>
            En savoir plus sur la version Production
          </Button>
        </>
      }
    >
      <p className="text-sm text-text-secondary">
        Les données saisies ressemblent à de vraies données de prix pharmaceutiques. Le mode
        Trial est réservé aux données illustratives.
      </p>
      <p className="text-xs text-text-tertiary mt-3">
        Si vous travaillez avec des données réelles, passez à la version Production pour
        bénéficier de la sécurité et de la conformité adaptées aux données confidentielles.
      </p>
    </Modal>
  );
}
