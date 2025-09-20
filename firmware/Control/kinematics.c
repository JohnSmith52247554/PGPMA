#include <math.h>
#include <stdint.h>

#include "kinematics.h"

#include "trigonometric.h"

#define DELTA_Y 17.4f
#define L1 19.8f
#define L2 14.6f
#define L3 34.f

#define THETA_1_MIN -PI
#define THETA_1_MAX PI
#define THETA_2_MIN (0.5f * PI)
#define THETA_2_MAX (1.5f * PI)
#define THETA_3_MIN (0.2f * PI)
#define THETA_3_MAX (1.6f * PI)
#define THETA_4_MIN (0.6f * PI)
#define THETA_4_MAX (1.4f * PI)

#define SQUARE(x) ((x) * (x))

#define DISTANCE_TOLERABLE_ERROR 0.1f
#define RADIAN_TOLERABLE_ERROR 1.f

#define pedestalHeight 20.0f
#define pedestalRadius 15.0f
#define axisHeight 5.0f
#define margin_of_deviation 0.0002f

float normalize(float num);
float normalize180(float num);
uint8_t examine_reverse_resolve_result(KineHandle *handle);
uint8_t checkArmValid(KineHandle *handle);

uint8_t kine_resolve(KineHandle *handle)
{
    float x_p = L1 * t_sin_radian(handle->theta_2) - L2 * t_sin_radian(handle->theta_2 + handle->theta_3) + L3 * t_sin_radian(handle->theta_2 + handle->theta_3 + handle->theta_4);
    float y_p = DELTA_Y - L1 * t_cos_radian(handle->theta_2) + L2 * t_cos_radian(handle->theta_2 + handle->theta_3) - L3 * t_cos_radian(handle->theta_2 + handle->theta_3 + handle->theta_4);

    handle->x = x_p * t_cos_radian(handle->theta_1);
    handle->y = y_p;
    handle->z = x_p * t_sin_radian(handle->theta_1);
    handle->alpha = handle->theta_2 + handle->theta_3 + handle->theta_4 - 5.f / 2.f * PI;

    // printf("x: %f, y: %f\nz: %f, a: %f\n", handle->x, handle->y, handle->z, handle->alpha);
    // fflush(stdout);

    return KINE_OK;
}

uint8_t kine_reverse_resolve(KineHandle *handle)
{
    // printf("X: %f, Y: %f\nZ: %f, A: %f\n", handle->x, handle->y, handle->z, handle->alpha);

    handle->theta_1 = t_arctan2_radian(handle->z, handle->x);
    handle->theta_1 = normalize180(handle->theta_1);

    const float x_p = sqrtf(SQUARE(handle->x) + SQUARE(handle->z));
    const float y_p = handle->y;

    const float C_1 = y_p - DELTA_Y - L3 * t_sin_radian(handle->alpha);
    const float C_2 = x_p - L3 * t_cos_radian(handle->alpha);
    // printf("C1: %f, C2: %f\n", C_1, C_2);

    const float arccos_x = (SQUARE(L1) + SQUARE(L2) - SQUARE(C_1) - SQUARE(C_2)) / (2 * L1 * L2);
    if (arccos_x > 1.f || arccos_x < -1.f)
        return KINE_UNREACHABLE;
    const float Q = t_arccos_radian(arccos_x);
    // printf("Q: %f\n", Q);

    // 情况1
    const float A = sqrtf(SQUARE(L1 - L2 * t_cos_radian(Q)) + SQUARE(L2 * t_sin_radian(Q)));
    // printf("A: %f\n", A);
    const float sin_beta_1 = -(L2 * t_sin_radian(Q)) / A;
    const float cos_beta_1 = (L1 - L2 * t_cos_radian(Q)) / A;
    float beta_1 = t_arcsin_radian(sin_beta_1);
    if (cos_beta_1 < 0.f)
    {
        beta_1 = PI - beta_1;
    }
    // printf("beta 1: %f\n", beta_1);

    // 情况1.1
    const float sin_var = C_2 / A;
    if (!(sin_var >= -1.f && sin_var <= 1.f))
    {
        return KINE_UNREACHABLE;
    }

    handle->theta_2 = t_arcsin_radian(sin_var) - beta_1;
    handle->theta_3 = Q;
    handle->theta_4 = handle->alpha + 5.f / 2.f * PI - Q - t_arcsin_radian(sin_var) + beta_1;
    handle->theta_2 = normalize(handle->theta_2);
    handle->theta_3 = normalize(handle->theta_3);
    handle->theta_4 = normalize(handle->theta_4);
    uint8_t examine_result = examine_reverse_resolve_result(handle);
    // printf("1.1\n");
    // printf("theta_1: %f, theta_2: %f\ntheta_3: %f, theta_4: %f\n", radian2degree(handle->theta_1), radian2degree(handle->theta_2), radian2degree(handle->theta_3), radian2degree(handle->theta_4));
    // printf("examine: %d\n\n", examine_result);
    if (examine_result == KINE_OK)
        return KINE_OK;

    // 情况1.2
    handle->theta_2 = PI - t_arcsin_radian(sin_var) - beta_1;
    handle->theta_3 = Q;
    handle->theta_4 = handle->alpha - Q + t_arcsin_radian(sin_var) + beta_1 + 3.f / 2.f * PI;
    handle->theta_2 = normalize(handle->theta_2);
    handle->theta_3 = normalize(handle->theta_3);
    handle->theta_4 = normalize(handle->theta_4);
    examine_result = examine_reverse_resolve_result(handle);
    // printf("1.2\n");
    // printf("theta_1: %f, theta_2: %f\ntheta_3: %f, theta_4: %f\n", radian2degree(handle->theta_1), radian2degree(handle->theta_2), radian2degree(handle->theta_3), radian2degree(handle->theta_4));
    // printf("examine: %d\n\n", examine_result);
    if (examine_result == KINE_OK)
        return KINE_OK;

    // 情况2
    const float sin_beta_2 = L2 * t_sin_radian(Q) / A;
    const float cos_beta_2 = (L1 - L2 * t_cos_radian(Q)) / A;
    float beta_2 = t_arcsin_radian(sin_beta_2);
    if (cos_beta_2 < 0.f)
    {
        beta_2 = PI - beta_2;
    }

    // 情况2.1
    handle->theta_2 = t_arccos_radian(sin_var) - beta_2;
    handle->theta_3 = -Q;
    handle->theta_4 = handle->alpha + 5.f / 2.f * PI - t_arcsin_radian(sin_var) + beta_2 + Q;
    handle->theta_2 = normalize(handle->theta_2);
    handle->theta_3 = normalize(handle->theta_3);
    handle->theta_4 = normalize(handle->theta_4);
    examine_result = examine_reverse_resolve_result(handle);
    // printf("2.1\n");
    // printf("theta_1: %f, theta_2: %f\ntheta_3: %f, theta_4: %f\n", radian2degree(handle->theta_1), radian2degree(handle->theta_2), radian2degree(handle->theta_3), radian2degree(handle->theta_4));
    // printf("examine: %d\n\n", examine_result);
    if (examine_result == KINE_OK)
        return KINE_OK;

    // 情况2.2
    handle->theta_2 = PI - t_arcsin_radian(sin_var) - beta_2;
    handle->theta_3 = -Q;
    handle->theta_4 = handle->alpha + 3.f / 2.f * PI + t_arcsin_radian(sin_var) + beta_2 + Q;
    handle->theta_2 = normalize(handle->theta_2);
    handle->theta_3 = normalize(handle->theta_3);
    handle->theta_4 = normalize(handle->theta_4);
    examine_result = examine_reverse_resolve_result(handle);
    // printf("2.2\n");
    // printf("theta_1: %f, theta_2: %f\ntheta_3: %f, theta_4: %f\n", radian2degree(handle->theta_1), radian2degree(handle->theta_2), radian2degree(handle->theta_3), radian2degree(handle->theta_4));
    // printf("examine: %d\n\n", examine_result);
    if (examine_result == KINE_OK)
        return KINE_OK;

    return examine_result;
}

MotorAngle get_motor_angle(KineHandle *handle)
{
    MotorAngle motor_angle;
    motor_angle.m1a = radian2degree(handle->theta_1);
    motor_angle.m2a = radian2degree(handle->theta_2 - PI);
    motor_angle.m3a = -radian2degree(handle->theta_3 - PI);
    motor_angle.m4a = radian2degree(handle->theta_4 - PI) - motor_angle.m3a;
    return motor_angle;
}

float normalize(float num)
{
    while (num < 0.f)
    {
        num += 2 * PI;
    }
    while (num >= 2.f * PI)
    {
        num -= 2 * PI;
    }
    return num;
}

float normalize180(float num)
{
    while (num < -PI)
    {
        num += 2 * PI;
    }
    while (num >= PI)
    {
        num -= 2 * PI;
    }
    return num;
}

uint8_t examine_reverse_resolve_result(KineHandle *handle)
{
    if (!(handle->theta_1 >= THETA_1_MIN && handle->theta_1 <= THETA_1_MAX))
        return KINE_JOINT_LIMIT;
    if (!(handle->theta_2 >= THETA_2_MIN && handle->theta_2 <= THETA_2_MAX))
        return KINE_JOINT_LIMIT;
    if (!(handle->theta_3 >= THETA_3_MIN && handle->theta_3 <= THETA_3_MAX))
        return KINE_JOINT_LIMIT;
    if (!(handle->theta_4 >= THETA_4_MIN && handle->theta_4 <= THETA_4_MAX))
        return KINE_JOINT_LIMIT;

    KineHandle handle_copy = *handle;
    kine_resolve(&handle_copy);
    if (fabsf(handle_copy.x - handle->x) > DISTANCE_TOLERABLE_ERROR)
        return KINE_INVALIDE;
    if (fabsf(handle_copy.y - handle->y) > DISTANCE_TOLERABLE_ERROR)
        return KINE_INVALIDE;
    if (fabsf(handle_copy.z - handle->z) > DISTANCE_TOLERABLE_ERROR)
        return KINE_INVALIDE;
    if (fabsf(handle_copy.alpha - handle->alpha) > RADIAN_TOLERABLE_ERROR)
        return KINE_INVALIDE;

    if (checkArmValid(handle) != KINE_OK)
        return KINE_ARM_COLLISION;

    return KINE_OK;
}

uint8_t checkArmValid(KineHandle *handle)
{
    float x1 = L1 * t_sin_radian(handle->theta_2);
    float y1 = -L1 * t_cos_radian(handle->theta_2);
    float x2 = x1 - L2 * t_sin_radian(handle->theta_2 + handle->theta_3);
    float y2 = y1 + L2 * t_cos_radian(handle->theta_2 + handle->theta_3);
    float x3 = x2 + L3 * t_sin_radian(handle->theta_2 + handle->theta_3 + handle->theta_4);
    float y3 = y2 - L3 * t_cos_radian(handle->theta_2 + handle->theta_3 + handle->theta_4);
    float A1, B1, A, B, C, intersection_x, intersection_y;

    // check axis2
    if (fabsf(x2) <= pedestalRadius + axisHeight)
    {
        if (y2 < axisHeight)
        {
            return KINE_INVALIDE;
        }
    }
    else
    {
        if (y2 < -pedestalHeight + axisHeight)
        {
            return KINE_INVALIDE;
        }
    }

    // check axis3
    if (fabsf(x3) <= pedestalRadius + axisHeight)
    {
        if (y3 < axisHeight)
        {
            return KINE_INVALIDE;
        }
    }
    else
    {
        if (y3 < -pedestalHeight + axisHeight)
        {
            return KINE_INVALIDE;
        }
    }
    if (fabsf(x3) <= pedestalRadius / 2.f)
    {
        if (y3 < pedestalHeight)
        {
            return KINE_INVALIDE;
        }
    }
    // check intersection

    A1 = -t_cos_radian(handle->theta_2);
    B1 = t_sin_radian(handle->theta_2);
    A = t_cos_radian(handle->theta_2 + handle->theta_3 + handle->theta_4);
    B = t_sin_radian(handle->theta_2 + handle->theta_3 + handle->theta_4);
    C = -t_sin_radian(handle->theta_2 + handle->theta_3 + handle->theta_4) * (-L1 * t_cos_radian(handle->theta_2) + L2 * t_cos_radian(handle->theta_2 + handle->theta_3)) - t_cos_radian(handle->theta_2 + handle->theta_3 + handle->theta_4) * (L1 * t_sin_radian(handle->theta_1) - L2 * t_sin_radian(handle->theta_2 + handle->theta_3));

    if (fabsf(A1) < margin_of_deviation)
    {
        intersection_y = 0.0;
    }
    else
    {
        intersection_y = -C * A1 / (B1 * A + B * A1);
    }
    if (fabsf(B1) < margin_of_deviation)
    {
        intersection_x = 0.0;
    }
    else
    {
        intersection_x = -C * B1 / (B1 * A + B * A1);
    }
    //	intersection_y = -C*A1/(B1*A+B*A1);
    //	intersection_x = -C*B1/(B1*A+B*A1);
    if (fabsf(x1) >= margin_of_deviation && ((intersection_x >= -axisHeight && intersection_x <= x1 + axisHeight) || (intersection_x <= axisHeight && intersection_x >= x1 - axisHeight)) || fabsf(y1) >= margin_of_deviation && ((intersection_y >= -axisHeight && intersection_y <= y1 + axisHeight) || (intersection_y <= axisHeight && intersection_y >= y1 - axisHeight)))
    {
        if (fabsf(x3 - x2) >= margin_of_deviation && ((intersection_x >= x2 - axisHeight && intersection_x <= x3 + axisHeight) || (intersection_x <= x2 + axisHeight && intersection_x >= x3 - axisHeight)) || fabsf(y3 - y2) >= margin_of_deviation && ((intersection_y >= y2 - axisHeight && intersection_y <= y3 + axisHeight) || (intersection_y <= y2 + axisHeight && intersection_y >= y3 - axisHeight)))
        {
            return KINE_INVALIDE;
        }
    }
    return KINE_OK;
}