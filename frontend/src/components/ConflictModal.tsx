import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";

type EntityType = "scenario" | "asset" | "country-data";

const ENTITY_LABELS: Record<EntityType, string> = {
  scenario: "scénario",
  asset: "asset",
  "country-data": "données pays",
};

interface ConflictModalProps {
  open: boolean;
  entityType: EntityType;
  onReload: () => void;
  onForceOverwrite: () => void;
  onCancel: () => void;
}

export function ConflictModal({
  open,
  entityType,
  onReload,
  onForceOverwrite,
  onCancel,
}: ConflictModalProps) {
  return (
    <Modal
      open={open}
      onClose={onCancel}
      title="Conflit de modification"
      size="sm"
      footer={
        <>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            Annuler
          </Button>
          <Button variant="danger" size="sm" onClick={onForceOverwrite}>
            Écraser quand même
          </Button>
          <Button variant="primary" size="sm" onClick={onReload}>
            Recharger
          </Button>
        </>
      }
    >
      <p className="text-sm text-text-secondary">
        Un autre utilisateur a modifié ce{" "}
        <span className="font-medium text-text-primary">{ENTITY_LABELS[entityType]}</span>{" "}
        depuis votre dernier chargement. Vos modifications n&apos;ont pas été sauvegardées.
      </p>
      <p className="text-xs text-text-tertiary mt-3 space-y-1">
        <span className="block">
          <strong className="text-text-secondary">Recharger</strong> — récupère la version
          actuelle (vos modifications locales seront perdues).
        </span>
        <span className="block">
          <strong className="text-text-secondary">Écraser</strong> — force votre version sur
          celle de l&apos;autre utilisateur. Cette action est auditée.
        </span>
      </p>
    </Modal>
  );
}
