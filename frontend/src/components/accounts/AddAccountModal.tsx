"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateAccount } from "@/hooks/useAccounts";

const accountSchema = z.object({
  username: z.string().min(1, "Username is required"),
  digest_enabled: z.boolean(),
  alerts_enabled: z.boolean(),
});

type AccountFormData = z.infer<typeof accountSchema>;

interface AddAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddAccountModal({ isOpen, onClose }: AddAccountModalProps) {
  const [error, setError] = useState<string | null>(null);
  const createAccount = useCreateAccount();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<AccountFormData>({
    resolver: zodResolver(accountSchema),
    defaultValues: {
      digest_enabled: true,
      alerts_enabled: true,
    },
  });

  const onSubmit = async (data: AccountFormData) => {
    try {
      setError(null);
      await createAccount.mutateAsync(data);
      reset();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create account");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Monitored Account">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
            {error}
          </div>
        )}

        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <Input
            id="username"
            placeholder="@username"
            {...register("username")}
          />
          {errors.username && (
            <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
          )}
        </div>

        <div className="flex gap-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="digest_enabled"
              {...register("digest_enabled")}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="digest_enabled" className="ml-2 text-sm text-gray-700">
              Enable Digest
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="alerts_enabled"
              {...register("alerts_enabled")}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="alerts_enabled" className="ml-2 text-sm text-gray-700">
              Enable Alerts
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={createAccount.isPending}>
            {createAccount.isPending ? "Adding..." : "Add Account"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

