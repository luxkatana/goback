export type Job = {
	created_at: Date,
	status_messages: {
		message: string,
		status_type: number
	}[],
	job_id: number
}

