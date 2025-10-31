import { Button, Field, Fieldset, Input, Link, Spinner, Text, VStack } from "@chakra-ui/react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link as RLink, useLocation, useNavigate } from "react-router-dom";

interface LoginFormInput {
	username: string,
	password: string

}

export default function Login() {
	const { register, handleSubmit, formState: { errors, isValid } } = useForm<LoginFormInput>({
		mode: "onChange",
	});
	const navigate = useNavigate();
	const [loading, setLoading] = useState<boolean>(false);
	const location = useLocation();
	function SubmitCallback(formdata: LoginFormInput) {
		if (loading == false) {
			setLoading(true);
			console.log(formdata);
			setLoading(false);
			const search = new URLSearchParams(location.search);
			const path = search.get("n");
			navigate(path !== null ? path : "/dashboard");
		}
	}
	return <>
		<VStack>
			<form onSubmit={handleSubmit(SubmitCallback)}>
				<Fieldset.Root size="lg" maxW="2xl" marginTop="20">

					<Fieldset.Legend fontSize="4xl">Login form</Fieldset.Legend>
					<Fieldset.HelperText fontSize="2xl" marginTop="10">
						<Link asChild colorPalette="yellow" _hover={{ color: "blue.500" }} variant="underline">
							<RLink to="/signup">Not a member yet?</RLink>
						</Link>

					</Fieldset.HelperText>
					<Fieldset.Content>
						<Field.Root>
							<Field.Label>Username</Field.Label>
							<Text color="red.fg">{errors.username && errors.username.message}</Text>
							<Input {...register("username", { required: "This field is required", maxLength: { value: 50, message: "Max 50 characters" }, minLength: { value: 10, message: "Min 10 characters" } })}
								size="2xl" placeholder="Your username" variant="subtle" name="username" />
						</Field.Root>

						<Field.Root>
							<Field.Label>Password</Field.Label>
							<Text color="red.fg">{errors.password && errors.password.message}</Text>
							<Input {...register("password",
								{
									required: "This field is required",
									minLength: { value: 8, message: "Minimal 8 characters" },
									maxLength: { value: 50, message: "Max 50 characters" }
								})}
								size="2xl" placeholder="Your password" variant="subtle" type="password" name="password" />
						</Field.Root>
						<Button marginTop={5} type="submit" disabled={!isValid}>Log in</Button>
					</Fieldset.Content>
				</Fieldset.Root>
			</form>
			{loading && <VStack>
				<Spinner marginTop={30} size="lg" />
				<Text marginTop={30}>Logging in...</Text>
			</VStack>}

		</VStack>
	</>

}
