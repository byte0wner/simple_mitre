#define PAM_SM_AUTH
#include <security/pam_modules.h>
#include <security/pam_ext.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>


const char *banner[] = {
	"\n██████╗  █████╗ ████████╗███████╗ █████╗ ███╗   ██╗                                  ",
	"██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗  ██║                                  ",
	"██████╔╝███████║   ██║   ███████╗███████║██╔██╗ ██║                                  ",
	"██╔═══╝ ██╔══██║   ██║   ╚════██║██╔══██║██║╚██╗██║                                  ",
	"██║     ██║  ██║   ██║   ███████║██║  ██║██║ ╚████║                                  ",
	"╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                                  ",
	"                                                                                     ",
	" ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     ██╗     ███████╗██████╗ ",
	"██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     ██║     ██╔════╝██╔══██╗",
	"██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     ██║     █████╗  ██████╔╝",
	"██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     ██║     ██╔══╝  ██╔══██╗",
	"╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗███████╗███████╗██║  ██║",
	" ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝\n",
	"\nТы блядина обожди вещи кидать свои на шконарь. Ну давай проверим, мужик ты или сука. Ответь на вопрос и можешь падать к пацанам. А коль вопрос не осилишь, то петухом будешь.\n"
};

const char * phrazi[5][2] = {
	{"Зеки рисуют на стене футбольные ворота, а на полу мяч. Говорят забить гол. ", "poproshu dat pas"},
	{"Бутылку разбивают и говорят: 'Зашей'. Что будешь делать? ", "poproshu vivernut naiznanku"},
	{"Ты упал в яму. В яме пирожок и хуй. Что съешь, что в жопу засунешь? ", "vozmu pirozhok i vilezu is yami"},
	{"Тебе дают в руки веник и говорят: 'Сыграй на гитаре что-нибудь'. ", "a ti nastroi snachala"},
	{"Просят сыграть на батарее, как на баяне. Что будешь делать? ", "poproshu razdut meha"},
};

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv) {
    const struct pam_conv *conv;
    struct pam_response *resp = NULL;
    int retval;
    int i;
    char *service = NULL;

    srand(time(NULL));
    int random_number = (rand() % 4) + 1;

    retval = pam_get_item(pamh, PAM_CONV, (const void **)&conv);
    if (retval != PAM_SUCCESS) {
        return retval;
    }

    pam_get_item(pamh, PAM_SERVICE, (const void **)&service);
    int is_graphical_login = 0;
    if (service) {
        if (strcmp(service, "lightdm") == 0 ||
            strcmp(service, "lightdm-greeter") == 0 ||
            strcmp(service, "lightdm-autologin") == 0) {
            is_graphical_login = 1;
        }
    }

    if (is_graphical_login) {
        struct pam_message mesg[2];
        const struct pam_message *mesg_ptr[2];

        mesg[0].msg_style = PAM_TEXT_INFO;
        mesg[0].msg = phrazi[random_number][0];

        mesg[1].msg_style = PAM_PROMPT_ECHO_ON;
        mesg[1].msg = "Сюда вводи нахуй";

        mesg_ptr[0] = &mesg[0];
        mesg_ptr[1] = &mesg[1];

        retval = conv->conv(2, mesg_ptr, &resp, conv->appdata_ptr);
        if (retval != PAM_SUCCESS || resp == NULL) {
            if (resp) free(resp);
            return PAM_CONV_ERR;
        }

        if (resp[1].resp == NULL) {
            if (resp[0].resp) free(resp[0].resp);
            free(resp);
            return PAM_AUTH_ERR;
        }

        if (strcmp(resp[1].resp, phrazi[random_number][1]) != 0) {
            free(resp[1].resp);
            if (resp[0].resp) free(resp[0].resp);
            free(resp);
            return PAM_AUTH_ERR;
        }

        free(resp[1].resp);
        if (resp[0].resp) free(resp[0].resp);
        free(resp);

        return PAM_SUCCESS;
    }

    struct pam_message msg[15];
    const struct pam_message *msg_ptr[15];

    for (i = 0; i < 14; i++) {
        msg[i].msg_style = PAM_TEXT_INFO;
        msg[i].msg = banner[i];
        msg_ptr[i] = &msg[i];
    }

    msg[14].msg_style = PAM_PROMPT_ECHO_ON;
    msg[14].msg = phrazi[random_number][0];
    msg_ptr[14] = &msg[14];

    retval = conv->conv(15, msg_ptr, &resp, conv->appdata_ptr);
    if (retval != PAM_SUCCESS || resp == NULL) {
        return retval != PAM_SUCCESS ? retval : PAM_CONV_ERR;
    }

    if (resp[14].resp == NULL) {
        goto cleanup;
    }

    if (strcmp(resp[14].resp, phrazi[random_number][1]) != 0) {
        goto cleanup_auth_err;
    }

    goto cleanup_success;

cleanup_auth_err:
    retval = PAM_AUTH_ERR;
    goto cleanup;

cleanup_success:
    retval = PAM_SUCCESS;
cleanup:
    if (resp) {
        for (i = 0; i < 15; i++) {
            if (resp[i].resp) {
                free(resp[i].resp);
            }
        }
        free(resp);
    }
    return retval;
}


PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv) {
    return PAM_SUCCESS;
}
                                                                                     