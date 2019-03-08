DO $$
BEGIN
	BEGIN
		PERFORM discount_type FROM account_invoice_line WHERE discount_type='percent' OR discount_type='amount' LIMIT 1;
		IF NOT FOUND THEN
			RETURN;
		END IF;
	EXCEPTION
	    WHEN OTHERS THEN
        RETURN;
	END;
	BEGIN
		ALTER TABLE account_invoice_line ADD COLUMN discount_amount NUMERIC DEFAULT 0;
	EXCEPTION
	    WHEN OTHERS THEN
        NULL;
	END;
	UPDATE account_invoice_line SET discount_amount = discount WHERE discount_type='amount';
	UPDATE account_invoice_line SET discount = 0.0 WHERE discount_type='amount';
	UPDATE account_invoice_line SET discount_type = 'deprecated' WHERE TRUE;
	
END $$