import { Button, Field, Fieldset, Input, Text, VStack } from "@chakra-ui/react";
import { useForm } from "react-hook-form";
interface SignupInput {
	username: string,
	email: string,
	password: string
}

export default function Signup() {

	const { register, handleSubmit, formState: { errors, isValid } } = useForm<SignupInput>({
		mode: "onChange"
	});
	function SignupCallback(data: SignupInput) {
		console.log(data);
	}
	return <VStack>
		<form onSubmit={handleSubmit(SignupCallback)}>
			<Fieldset.Root size="lg">
				<Fieldset.Legend fontSize="4xl" marginTop={10}>Signup Form</Fieldset.Legend>
				<Fieldset.Content>
					<Field.Root>
						<Field.Label marginTop={5}>Username</Field.Label>

						<Text color="red.fg">{errors.username && errors.username.message}</Text>
						<Input {...register("username", {
							required: "This field is required",
							maxLength: { value: 50, message: "Max 50 characters" },
							minLength: { value: 10, message: "Min 10 characters" }
						})}
							size="2xl" placeholder="Your username" variant="subtle" name="username" />
					</Field.Root>

					<Field.Root>
						<Field.Label>Email</Field.Label>
						<Text color="red.fg">{errors.email && errors.email.message}</Text>
						<Input {...register("email", {
							maxLength: 255,
							required: "This field is required",
							pattern: {
								value: /(?:[a-z0-9!#$%&'*+\x2f=?^_`\x7b-\x7d~\x2d]+(?:\.[a-z0-9!#$%&'*+\x2f=?^_`\x7b-\x7d~\x2d]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9\x2d]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9\x2d]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9\x2d]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/,
								message: "Email should be valid (e.g hello@gmail.com)"
							},

						})} placeholder="Your email" type="email" />
					</Field.Root>
					<Field.Root>
						<Field.Label>Password</Field.Label>
						<Text color="red.fg">{errors.password && errors.password.message}</Text>
						<Input {...register("password", {
							required: "This field is required",
							minLength: 8,
							maxLength: 50,
						})} placeholder="Password" type="password" />
					</Field.Root>
					<Button type="submit" disabled={!isValid}>Create an account</Button>
				</Fieldset.Content>
			</Fieldset.Root>

		</form>


	</VStack >
}
