import { useContext, useState } from "react"
import { AuthContext, CreateBackupCall } from "../utils/AuthContext"
import { useForm } from "react-hook-form";
import { Button, Field, Fieldset, Input, Spinner, Text, VStack } from "@chakra-ui/react";
import type { AxiosError } from "axios";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

type CreationFormType = {
	url: string
}
export default function CreateBackupPage() {
	const auth_context = useContext(AuthContext);
	const [loadingpage, setloadingpage] = useState<boolean>(false);
	const { register, formState: { errors, isValid }, handleSubmit } = useForm<CreationFormType>({ mode: "onChange" });
	const navigate = useNavigate();
	async function SubmitCallback(data: CreationFormType) {
		if (loadingpage == false) {
			setloadingpage(true);
			try {
				const job_id: number = await CreateBackupCall(data.url, auth_context);
				toast(`Sweet! Currently busy working on it, job id: ${job_id} `);
				navigate(`/job?job_id=${job_id}`);

			} catch (e: AxiosError | any) {
				toast.error(e);
			}
			setloadingpage(false);

		}


	}
	return <>
		<VStack>
			<form onSubmit={handleSubmit(SubmitCallback)}>
				<Fieldset.Root>
					<Fieldset.Legend fontSize="4xl" marginTop="10">Create a backup of a page </Fieldset.Legend>


					<Fieldset.Content>
						<Field.Root>
							<Field.Label>The url</Field.Label>
							<Text color="red.fg">{errors.url && errors.url.message}</Text>
							<Input {...register("url", {
								required: "This field is required",
								maxLength: {
									value: 100,
									message: "Max 100 characters (perhaps remove tracking query params?)"
								},
								pattern: {
									value: /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$/,
									message: "Must be an url (e.g https://guthib.com)"
								}
							})} placeholder="The url (e.g https://guthib.com)" type="url" />
						</Field.Root>
						<Button type="submit" disabled={!isValid}>Send a backup request</Button>
					</Fieldset.Content>
				</Fieldset.Root>

			</form>
			{loadingpage && <VStack>
				<Spinner marginTop={30} size="lg" />
				<Text marginTop={30}>Doing magic stuff 💫</Text>

			</VStack>}

		</VStack>


	</>
}
